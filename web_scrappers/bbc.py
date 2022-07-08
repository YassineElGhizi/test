import requests
import json
from global_params import *
from bs4 import BeautifulSoup as BS
from web_scrappers.helpers import get_main_menu_links, check_if_it_contains_submenu, get_api_url

GLOBAL_SESSION = requests.session()


def get_main_menu_and_their_links():
    print('[+] Getting main_menus & their links')
    res = GLOBAL_SESSION.get(website_target, headers=headers)
    soup = BS(res.text, features="html.parser")

    main_menu = soup.findAll('li', {
        'class': 'gs-o-list-ui__item--flush gel-long-primer gs-u-display-block gs-u-float-left nw-c-nav__wide-menuitem-container'}
                             )

    return list(map(get_main_menu_links, main_menu))


def collect_data(main_menu_and_their_links):
    for m in main_menu_and_their_links:
        res = GLOBAL_SESSION.get(m["link"], headers=headers)
        soup = BS(res.text, features="html.parser")
        if check_if_it_contains_submenu(soup):
            print(f'link = {m["link"]} has a sub menu')
        else:
            res2 = GLOBAL_SESSION.get(get_api_url(soup), headers=api_headers)
            json_response = json.loads(res2.text)
            results = json_response['payload'][0]['body']['results']
            for r in results:
                print(f'dateAdded = {r["dateAdded"]}')
                print(f'url = {r["url"]}')
                print(f'image = {r["image"]["href"]}')
                print(f'summary = {r["summary"]}')
                print(f'title = {r["title"]}')
                try:
                    print(f'contributor_name = {r["contributor"]["name"]}')
                except KeyError:
                    print(f'contributor_name = {None}')
                try:
                    print(f'contributor_role= {r["contributor"]["role"]}')
                except KeyError:
                    print(f'contributor_role= {None}')
                print("\n")
        quit()


if __name__ == '__main__':
    collect_data(get_main_menu_and_their_links())
