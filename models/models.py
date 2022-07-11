from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class News:
    dateAdded: datetime
    url: str
    images: List[str]
    title: str
    sub_title: str
    content: str
    related_topics: List[str]
    menu_name: str
    sub_menu_name: str = None
    contributor_name: str = None
    contributor_role: str = None
    videos: List[str] = None
