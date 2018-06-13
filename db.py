# -*- coding: utf-8 -*-
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from pymongo import MongoClient

client = MongoClient()

MongoDB_URI = os.environ['MONGODB_URI']
# MongoDB_URI = 'mongodb://localhost:27017/testdb'
DB_NAME = MongoDB_URI.split('/')[-1]

client = MongoClient(MongoDB_URI)

db = client[DB_NAME]
optionsCollection = db['options']
userCollection = db['user']
chatCollection = db['chat']
matchCollection = db['match']

logger.info("DB ready!")


def loadOpenMatches():
    filterObj = {
        'result': 'O'
    }
    cursor = matchCollection.find(filterObj)
    matches = []
    for m in cursor:
        matches.append(m)
    return matches

def updateMatch(matchId, matchObj):
    filterObj = {
        "matchId": matchId,
        # "chatId": chatId
    }
    updateObj = {
        '$set': matchObj
    }
    result = matchCollection.update_one(filterObj, updateObj, upsert=True)
    if result.matched_count:
        logger.info("Updated match with id {}".format(matchId))


def getUser(chatId, userId):
    filterObj = {
        "userId": userId,
        # "chatId": chatId
    }
    userObj = userCollection.find_one(filterObj)
    if userObj == None:
        updateObj = {
            '$set': {'userId': userId, 'bets': [], 'score': 0, 'toBetMatchId': ''}
        }
        setUserFields(chatId, userId, updateObj)  # set the default values for the user
        userObj = userCollection.find_one(filterObj)
    if 'bets' not in userObj.keys():
        updateObj = {
            '$set': {'bets': []}
        }
        setUserFields(chatId, userId, updateObj)  # set the default values for the user
        userObj = userCollection.find_one(filterObj)
    if 'score' not in userObj.keys():
        updateObj = {
            '$set': {'score': 0}
        }
        setUserFields(chatId, userId, updateObj)  # set the default values for the user
        userObj = userCollection.find_one(filterObj)
    if 'toBetMatchId' not in userObj.keys():
        updateObj = {
            '$set': {'toBetMatchId': ''}
        }
        setUserFields(chatId, userId, updateObj)  # set the default values for the user
        userObj = userCollection.find_one(filterObj)

    return userObj

def setUserFields(chatId, userId, updateObj):
    filterObj = {
        "userId": userId,
        # "chatId": chatId
    }
    # updateObj = {
    #     '$set': {'lang': lang}
    # }
    result = userCollection.update_one(filterObj, updateObj, upsert=True)
    if result.matched_count:
        logger.info("Updated the field values for user with id {}".format(userId))
    return result


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

def updateUserScores():
    pass