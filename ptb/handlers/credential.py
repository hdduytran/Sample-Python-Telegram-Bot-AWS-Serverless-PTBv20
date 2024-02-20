import pymongo
import os

client = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = client['Humanizer']
col_users = db['users']

def get_user(user_id):
    return col_users.find_one({"user_id": user_id})

def update_user(user_id, data):
    col_users.update_one({"user_id": user_id}, {"$set": data}, upsert=True)