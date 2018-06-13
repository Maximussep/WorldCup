# -*- coding: utf-8 -*-
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from pymongo import MongoClient

client = MongoClient()

MongoDB_URI = os.environ['MONGODB_URI']
#MongoDB_URI = 'mongodb://localhost:27017/testdb'
DB_NAME = MongoDB_URI.split('/')[-1]

client = MongoClient(MongoDB_URI)

db = client[DB_NAME]
optionsCollection = db['options']


def getOptions(chatId, userId):
    filterObj = {
        # "userId": userId,
        "chatId": chatId
    }
    return optionsCollection.find_one(filterObj)


def setLang(chatId, userId, lang="en"):
    filterObj = {
        # "userId": userId,
        "chatId": chatId
    }
    updateObj = {
        '$set': {'lang': lang}
    }
    result = optionsCollection.update_one(filterObj, updateObj, upsert=True)
    if result.matched_count:
        logger.info("Set the language for chat with id {} to {}".format(chatId, lang))
    return lang


def getLang(chatId, userId):
    opts = getOptions(chatId, userId)
    if opts == None or not opts['lang']:
        lang = setLang(chatId, userId)  # set the default lang
    else:
        lang = opts['lang']
    return lang