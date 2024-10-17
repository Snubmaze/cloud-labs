from pymongo import MongoClient
from pprint import pprint
import time

MONGO_URL = "mongodb://mongo:27017"
client = MongoClient(MONGO_URL)
db = client.admin
dbs_list = db.command("listDatabases")
pprint(dbs_list)
time.sleep(180) #это нужно для того чтоб контейнер не сразу завершал свою работу
