import requests
from global_params import *
from bs4 import BeautifulSoup as BS
from web_scrappers.helpers import get_main_menu_links, check_if_it_contains_submenu, scrap_news
from web_scrappers.global_params import VIDEOS_MENU, STORIES, TV, NEWSBEAT

GLOBAL_SESSION = requests.session()


def get_main_menu_and_their_links():
    print('[+] Getting main_menus & their links')
    res = GLOBAL_SESSION.get(website_target, headers=headers)
    soup = BS(res.text, features="html.parser")

    main_menu = soup.findAll('li', {
        'class': 'gs-o-list-ui__item--flush gel-long-primer gs-u-display-block gs-u-float-left nw-c-nav__wide-menuitem-container'})

    return list(map(get_main_menu_links, main_menu))


def collect_data(main_menu_and_their_links):
    # For each main menu(name & link)
    for m in main_menu_and_their_links:
        try:

            # SKIPPING THE FOLLOWING BECAUSE THEY DONT HAVE ARTICLES
            if m["link"] in [VIDEOS_MENU, STORIES, TV, NEWSBEAT]:
                continue

            res = GLOBAL_SESSION.get(m["link"], headers=headers)
            soup = BS(res.text, features="html.parser")
            flag = check_if_it_contains_submenu(soup)
            if flag:  # IF THE MENU HAS A SUB MENU
                sub_navs = soup.find('nav', {'class': 'nw-c-nav__wide-secondary'})
                current = ((sub_navs.find('span').get_text()).replace(' selected', '')).strip().lower().replace(' ',
                                                                                                                '_')
                lis = [
                    {
                        "name": f"{li.get_text()}",
                        "link": f"{prefix}{li.find('a').get('href')}"}
                    for li in sub_navs.findAll('li') if li.get_text() != 'More More sections'
                ]
                print(f'applying scrap_news() on {m["link"]} -- 1st SubMenu')
                scrap_news(soup, GLOBAL_SESSION, m["menu"], current)
                for sub_cat in lis:
                    sub_cat_res = GLOBAL_SESSION.get(sub_cat["link"], headers=headers)
                    sub_cat_soup = BS(sub_cat_res.text, features='html.parser')
                    print(f'applying scrap_news() on {sub_cat["link"]} -- SubMenu Items')
                    scrap_news(sub_cat_soup, GLOBAL_SESSION, m["menu"], sub_cat["name"])
            else:  # IF THE MENU DO NOT HAVE A SUB MENU
                print(f'Applying scrap_news() on {m["link"]} -- SubMenu Elements')
                scrap_news(soup, GLOBAL_SESSION, m["menu"], None)
        except Exception as e:
            print(f'Exception= {e}')


if __name__ == '__main__':
    collect_data(get_main_menu_and_their_links())
