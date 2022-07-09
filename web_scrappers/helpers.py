import json
from datetime import datetime

from global_params import prefix, api_prefix, api_headers


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


def get_api_url(soup):
    print('\t[+] Getting API url')
    scripts = soup.findAll('script')
    target = ''
    for z in scripts:
        if "Morph.toInit.payloads.push(function() { Morph.setPayload('/data/bbc-morph-lx-commentary" in z.get_text():
            target = z.get_text()
            break

    if target:
        target = target.split("Morph.setPayload('")[-1]
        target = target.split(", {")[0]
        target = target.replace("'", "")
        return f'{api_prefix}{target}'


def scrap_news(soup, session, ):
    print(f'link = {get_api_url(soup)}')
    res2 = session.get(get_api_url(soup), headers=api_headers)
    json_response = json.loads(res2.text)
    results = json_response['payload'][0]['body']['results']
    list_results = []
    for r in results:
        firstPublished = datetime.strptime(r["firstPublished"].split('T')[0], "%Y-%m-%d")
        url = r["url"]
        image = r["image"]["href"]
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
        print(f'firstPublished = {firstPublished}')
        print(f'{(datetime.now() - firstPublished).days} days old')
        print("\n")
