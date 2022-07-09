import json

from datetime import datetime
from random import randint
from time import sleep
from global_params import headers
from bs4 import BeautifulSoup as BS

from global_params import prefix, api_prefix, api_headers, historical_time_line_in_months
from models.models import News
from mongodb.insert import insert_one, check_if_exists


def get_main_menu_links(soup):
    try:
        href = soup.find('a').get('href')
        link = f'{prefix}{href}'
        name = soup.get_text().strip().lower().replace(' ', '_')
        return {'menu': name, 'link': link}
    except Exception as e:
        print(f'[-] Exception : {e}')


def check_if_it_contains_submenu(soup) -> bool:
    exists = soup.findAll('nav', {'class': 'nw-c-nav__wide-secondary'})
    if not len(exists):
        return False
    return True


def get_api_url(soup, page_number: int) -> str:
    print('\t[+] Getting API url')
    scripts = soup.findAll('script')
    target = ''
    for z in scripts:
        if "Morph.toInit.payloads.push(function() { Morph.setPayload('/data/bbc-morph-lx-commentary" in z.get_text():
            target = z.get_text()
            break

    if target:
        v = '/version/'
        page = 'pageNumber/'
        target = target.split("Morph.setPayload('")[-1]
        target = target.split(", {")[0]
        target = target.replace("'", "")
        link_with_category_static_page_number = f'{api_prefix}{target}'
        link_version = link_with_category_static_page_number.split(f'{v}')[-1]
        prefix = link_with_category_static_page_number.split(f'{page}')[0]
        return f'{prefix}{page}{page_number}{v}{link_version}'


def scrap_news(soup, session, menu_name, sub_menu_name):
    print(f'\t\tlink = {get_api_url(soup, 1)}')
    list_results = []
    scraped_links = check_if_exists()
    for i in range(1, 100):
        print(f'\t\t\t[+] Scraping page: {i}')
        res2 = session.get(get_api_url(soup, i), headers=api_headers)
        json_response = json.loads(res2.text)
        results = json_response['payload'][0]['body']['results']
        stop_paginating = False
        for r in results:
            tmp_d = {}
            dateAdded = datetime.strptime(r["dateAdded"].split('T')[0], "%Y-%m-%d")
            try:
                url = f'https://www.bbc.com{r["url"]}'
            except KeyError:
                continue
            summary = r["summary"]
            title = r["title"]
            try:
                contributor_name = r["contributor"]["name"]
            except KeyError:
                contributor_name = None
            try:
                contributor_role = r["contributor"]["role"]
            except KeyError:
                contributor_role = None
            print(f'dateAdded = {dateAdded}')
            print(f'menu_name = {menu_name}')
            print(f'sub_menu_name = {sub_menu_name}')
            print(f'url = {url}')
            print(f'title = {title}')
            print(f'{(datetime.now() - dateAdded).days} days old', '\n')
            tmp_d["dateAdded"] = dateAdded
            tmp_d["url"] = url
            tmp_d["summary"] = summary
            tmp_d["title"] = title
            tmp_d["menu_name"] = menu_name
            tmp_d["sub_menu_name"] = sub_menu_name
            tmp_d["contributor_name"] = contributor_name
            tmp_d["contributor_role"] = contributor_role
            list_results.append(tmp_d)

            if (datetime.now() - dateAdded).days >= historical_time_line_in_months * 30:
                stop_paginating = True
                break
        if stop_paginating:
            break
        sleep(randint(3, 5))
    scrap_itme(list_results, session, scraped_links)


def scrap_itme(list_results, session, scraped_links):
    for i in list_results:
        if i["url"] in scraped_links:
            print('url already got scraper , Passing !!')
            continue
        print(f'i["url"] = {i["url"]}')
        res = session.get(f'{i["url"]}', headers=headers)
        soup = BS(res.text, features='html.parser')
        article = soup.find('article')
        images = [img.find('img').get('src') for img in article.findAll('div', {'data-component': 'image-block'})]
        p_txt = [p.text for p in article.findAll('div', {'data-component': 'text-block'})]
        content = "\n".join(p_txt)
        if len(p_txt) == 0:
            try:
                content = article.find('div', {'aria-live': 'polite'}).get_text()
            except AttributeError:
                continue
        try:
            related = soup.find('section', {'data-component': 'tag-list'})
            list_related = [li.text for li in related.findAll('li')]
        except:
            list_related = []

        i["images"] = images
        i["content"] = content
        i["related_topics"] = list_related
        n = News(**i)
        insert_one(n)
        sleep(randint(3, 5))
