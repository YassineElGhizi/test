from typing import List

from mongodb.conn import collection
from models.models import News


def insert_one(news: News):
    c = collection()
    c.insert_one(news.__dict__)


def check_if_exists() -> List[str]:
    c = collection()
    return [link["url"] for link in c.find({}, {"url": 1, "_id": 0})]
