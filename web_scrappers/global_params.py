headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    'accept': '*/*',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9',
    'DNT': '1',
    'Referer': 'https://google.com'
}

api_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    'accept': '*/*',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9',
    'DNT': '1',
    'Referer': 'https://www.bbc.co.uk',
    'Content-Type': 'application/json'
}

website_target = 'https://www.bbc.com/news'
prefix = 'https://www.bbc.com'
api_prefix = 'https://push.api.bbci.co.uk/batch?t='
historical_time_line_in_months = 3
VIDEOS_MENU = 'https://www.bbc.com/news/av/10462520'
STORIES = 'https://www.bbc.com/news/stories'
TV = 'https://www.bbc.com/news/world_radio_and_tv'
NEWSBEAT = 'https://www.bbc.com/news/newsbeat'
MIN_WAITING = 1
MAX_WAITING = 3
