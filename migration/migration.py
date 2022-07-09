from dataclasses import dataclass

import pymongo


@dataclass
class Db:
    db_created: bool


CLIENT = pymongo.MongoClient("mongodb://localhost:27017/")
DATABASE_NAME = 'test_bbc'
COLLECTION = 'test'

if __name__ == '__main__':
    db = CLIENT[f"{DATABASE_NAME}"]
    collection = db[f"{COLLECTION}"]
    x = Db(db_created=True)
    collection.insert_one(x.__dict__)
