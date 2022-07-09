import pymongo

CLIENT = pymongo.MongoClient("mongodb://localhost:27017/")
DATABASE_NAME = 'bbc'
COLLECTION = 'news'


def collection():
    db = CLIENT[f"{DATABASE_NAME}"]
    return db[f"{COLLECTION}"]
