import json
from json import JSONDecoder
from datetime import datetime
from random import randint
from time import sleep
from bs4 import BeautifulSoup as BS

import requests.exceptions

from global_params import prefix, api_prefix, api_headers, historical_time_line_in_months, MIN_WAITING, MAX_WAITING, \
    headers
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


def check_if_it_contains_submenu(soup):
    return soup.findAll('nav', {'class': 'nw-c-nav__wide-secondary'})


def get_api_url(soup, page_number: int) -> str:
    """
    Function responsible for extracting the API url from the html soup after for each given page number
    :param soup:
    :param page_number:int
    :return: str
    """
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
    """
    Scraping data from both API and Article main page and storing it into DB
    :param soup:
    :param session:
    :param menu_name:
    :param sub_menu_name:
    :return:
    """
    print(f'\t\tAPI_link = {get_api_url(soup, 1)}')
    list_results = []
    scraped_links = check_if_exists()  # Get the links of already scraped articles from DB to avoid article duplication
    for i in range(1, 50):  # Paginating API to get historical data (MAX API Pagination is 50)
        print(f'\t\t\t[+] Scraping page: {i}')
        try:
            res2 = session.get(get_api_url(soup, i), headers=api_headers)
        except requests.exceptions.MissingSchema:
            print(f'requests.exceptions.MissingSchema')
            break
        json_response = json.loads(res2.text)
        results = json_response['payload'][0]['body']['results']
        stop_paginating = False
        print(f'len(results) = {len(results)}')
        if i == 0 and len(results) == 0:
            # If the API returns nothing => means that the page content is LIVE so use another approach with handle_live_function()
            list_results = handle_live_news(soup, menu_name, sub_menu_name, session)
            break

        for r in results:
            tmp_d = {}
            dateAdded = datetime.strptime(r["dateAdded"].split('T')[0], "%Y-%m-%d")
            try:
                url = f'https://www.bbc.com{r["url"]}'
            except KeyError:
                continue
            title = r["title"]
            try:
                contributor_name = r["contributor"]["name"]
            except KeyError:
                contributor_name = None
            try:
                contributor_role = r["contributor"]["role"]
            except KeyError:
                contributor_role = None
            print(f'title = {title}, menu_name = {menu_name}, sub_menu_name = {sub_menu_name}, url = {url}')
            print(f'{(datetime.now() - dateAdded).days} days old', '\n')
            tmp_d["dateAdded"] = dateAdded
            tmp_d["url"] = url
            tmp_d["sub_title"] = title
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
        sleep(randint(MIN_WAITING, MAX_WAITING))
    # Open each Article separately to get content
    scrap_itme(list_results, session, scraped_links)


def scrap_itme(list_results, session, scraped_links):
    """
    Opens each article to get content, related topics...
    :param list_results:
    :param session:
    :param scraped_links:
    :return:
    """
    for i in list_results:
        if i["url"] in scraped_links:
            print('url already got scraper , Passing !!')
            continue
        print(f'i["url"] = {i["url"]}')
        res = session.get(f'{i["url"]}', headers=headers)
        soup = BS(res.text, features='html.parser')
        article = soup.find('article')
        title = soup.find('h1').get_text().strip()
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

        i["title"] = title
        i["images"] = images
        i["content"] = content
        i["related_topics"] = list_related
        # Creating an instance of News to validate data before storing it to DB
        n = News(**i)
        insert_one(n)
        sleep(randint(MIN_WAITING, MAX_WAITING))


def handle_live_news(soup, menu_name, sub_menu_name, session):
    """
    Handling live news
    :param soup:
    :param menu_name:
    :param sub_menu_name:
    :param session:
    :return:
    """
    paginate = True
    first_iter = True
    list_results = []
    while paginate:
        try:
            if not paginate:
                break
            if first_iter:
                scripts = soup.findAll('script')
                first_iter = False
            else:
                r = session.get(next_page_href, headers=headers)
                soup = BS(r.text, features='html.parser')
                scripts = soup.findAll('script')
            target = ''
            usefull_json_data = []
            next_page_href = soup.find('a', {
                'class': 'lx-pagination__btn gs-u-mr+ qa-pagination-next-page lx-pagination__btn--active'}).get('href')
            next_page_href = f'https://www.bbc.com/{next_page_href}'
            for z in scripts:
                if "Morph.toInit.payloads.push(function() { Morph.setPayload('/data/bbc-morph-lx-commentary" in z.get_text():
                    target = z.get_text()
                    break

            for j in extract_json_objects(target):
                usefull_json_data.append(j)
            list_data_dicts = usefull_json_data[0]
            list_data_dicts = list_data_dicts["body"]["results"]

            if len(list_data_dicts) == 0:
                paginate = False

            for n, r in enumerate(list_data_dicts):
                tmp_d = {}
                dateAdded = datetime.strptime(r["dateAdded"].split('T')[0], "%Y-%m-%d")
                try:
                    url = f'https://www.bbc.com{r["url"]}'
                except KeyError:
                    continue
                title = r["title"]
                try:
                    contributor_name = r["contributor"]["name"]
                except KeyError:
                    contributor_name = None
                try:
                    contributor_role = r["contributor"]["role"]
                except KeyError:
                    contributor_role = None
                print(f'title = {title}, menu_name = {menu_name}, sub_menu_name = {sub_menu_name}, url = {url}')
                print(f'{(datetime.now() - dateAdded).days} days old', '\n')
                tmp_d["dateAdded"] = dateAdded
                tmp_d["url"] = url
                tmp_d["sub_title"] = title
                tmp_d["menu_name"] = menu_name
                tmp_d["sub_menu_name"] = sub_menu_name
                tmp_d["contributor_name"] = contributor_name
                tmp_d["contributor_role"] = contributor_role
                list_results.append(tmp_d)

                if (datetime.now() - dateAdded).days >= historical_time_line_in_months * 30:
                    paginate = False
                    break
        except:
            return list_results
    return list_results


def extract_json_objects(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON datas
    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object."""
    pos = 0
    while True:
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1
