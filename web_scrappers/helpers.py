from global_params import prefix, api_prefix


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
