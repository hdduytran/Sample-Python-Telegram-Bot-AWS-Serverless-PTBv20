import pymongo
import os

client = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = client['Humanizer']
col_users = db['users']

def get_user(username):
    return col_users.find_one({"username": username})

def update_user(username, data):
    col_users.update_one({"username": username}, {"$set": data}, upsert=True)