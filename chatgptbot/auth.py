import os
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
whitelist_path = os.path.join(dir_path,'../whiteList.json')

with open(whitelist_path, 'r') as file:
    whiteList = json.load(file)
    user_ids = whiteList['users']
    chat_ids = whiteList['chats']


def checkChat(chat):
    if chat.id in chat_ids:
        return True;

def checkUser(user_id):
    if user_id in user_ids:
        return True

