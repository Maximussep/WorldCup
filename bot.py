# coding=utf-8
# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
import numpy as np
from telebot import types
import pymongo
import db
import os
from operator import itemgetter, attrgetter, methodcaller
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_TOKEN = os.environ['TELEGRAM_TOKEN']
# API_TOKEN = "602234037:AAEnaoUclYiYF_7E7mP3zerwxWDX2Ldrw_E"
# API_TOKEN = "450979982:AAEymX_wZh5kX1JD1-Ekb0CrF_xdCl-4LEQ"

bot = telebot.TeleBot(API_TOKEN)

logger.info("TG bot ready (API key: {})!".format(API_TOKEN))

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, """\
سلام، بات پیش‌بینی جام‌جهانی ۲۰۱۸ هستم!
برای آشنایی و نحوه‌ی امتیاز دهی /help را انتخاب کنید.
برای پیش‌بینی مسابقات امروز /openbets را انتخاب کنید.

You can change the language to English by pressing /english!
\
""")
    userObj = db.getUser(message.chat.id, message.from_user.id)
    if userObj['first'] == []:
        updateObj = {
            '$set': {'first': message.from_user.first_name}
        }
        db.setUserFields(message.chat.id, message.from_user.id, updateObj)
    if userObj['last'] == []:
        updateObj = {
            '$set': {'last': message.from_user.last_name}
        }
        db.setUserFields(message.chat.id, message.from_user.id, updateObj)
    print(userObj)


@bot.message_handler(commands=['help'])
def instructions(message):
    userObj = db.getUser(message.chat.id, message.from_user.id)
    if userObj['lang'] == "fa":
        bot.reply_to(message, """\
        بات /WorldCup1818bot جهت برگزاری مسابقات پیش‌بینی در گروه‌های تلگرام طراحی شده است. این بات را به گروه‌های خود اضافه کنید و در مسابقه‌ی پیش‌بینی جام‌جهانی شرکت کنید.

شما با انتخاب /openbets می‌توانید پیش‌بینی بازی‌هایی که هنوز پیش‌بینی نکرده‌اید را انجام دهید.
        
اگر نتیجه‌ی موردنظرتان در گزینه‌ها نبود، باید نتیجه را به صورت دستی با همان فرمت سایر نتایج وارد کنید. (اعداد به انگلیسی و جدا کردن به وسیله‌ی دونقطه)
        
نحوه‌ی امتیازدهی
پیش‌بینی درست نتیجه = ۲۵ امتیاز
پیش‌بینی درست گل‌های تیم برنده = ۱۸ امتیاز
پیش‌بینی درست اختلاف گل = ۱۵ امتیاز
پیش‌بینی درست گل‌های تیم بازنده = ۱۲ امتیاز
پیش‌بینی درست تیم برنده = ۱۰ امتیاز
پیش‌بینی نتیجه‌ی مساوی = ۴ امتیاز
(در صورت مساوی نشدن بازی)
        \
        """)
    else:
        bot.reply_to(message, """\
        Add /WorldCup1818bot to your groups and compete with your family and friends.
        
You can start betting by pressing /openbets.
        
For group stage, you will earn 10 points if you get the exact right score, 7 points for guessing the difference right and 5 points if you only get the winner right.
        \
        """)


@bot.message_handler(commands=['openbets', 'changebet'])
def show_games(message):
    markup = types.ReplyKeyboardMarkup()
    userObj = db.getUser(message.chat.id, message.from_user.id)
    if message.text == '/changebet':
        wantToHaveNewBet = False
        wantToChangeBet = True
    else:
        wantToHaveNewBet = True
        wantToChangeBet = False
    matches = db.loadOpenMatches()

    openBets = []
    for match in matches:
        alreadyBet = False
        for bet in userObj['bets']:
            if bet['matchId'] == match['matchId']:
                alreadyBet = True
                break
        if (alreadyBet and wantToChangeBet) or (not alreadyBet and wantToHaveNewBet):
            openBets.append(match)

    open_text = "لطفاً بازی‌ موردنظر را انتخاب کنید یا برای تغییر نتیجه "
    open_text += "/changebet"
    open_text += " را فشار دهید:"
    open_text += '\nPlease choose the game you want to bet on or choose /changebet:'
    if  openBets != []:
        for Obet in openBets:
            itembtn1 = Obet['flags']
            markup.row(itembtn1)
        bot.send_message(chat_id=message.from_user.id, text= open_text, reply_markup=markup)
    else:
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(chat_id=message.from_user.id, text="""\
        همه‌ی بازی‌ها را پیش‌بینی کردید! برای تغییر نتایج /changebet را انتخاب کنید.

You have no open bets. Press /changebet to change your bets.
                   \
                   """, reply_markup=markup)


@bot.message_handler(commands=['ImIn@WorldCup1818bot'])
def ImIn(message):
    chatObj = db.getChat(message.chat.id)
    chatObj.append(message.from_user.id)


@bot.message_handler(commands=['language'])
def choose_language(message):
    markup = types.ReplyKeyboardMarkup()
    itembtnfar = types.KeyboardButton('فارسی')
    itembtneng = types.KeyboardButton('/english')
    markup.row(itembtnfar, itembtneng)
    bot.send_message(chat_id=message.chat.id, text="Please choose your preferred language:", reply_markup=markup)


@bot.message_handler(commands=['english'])
def set_english(message):
    db.setLang(message.chat.id, message.from_user.id, "en")
    markup = types.ReplyKeyboardRemove(selective=False)
    updateObj = {
        '$set': {'lang': "en"}
    }
    db.setUserFields(message.chat.id, message.from_user.id, updateObj)
    bot.send_message(message.chat.id, "Sure, I'll speak to you in English! \nYou can press /help for bot instruction. \nYou can press /openbets to start betting.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'فارسی')
def set_language(message):
    db.setLang(message.chat.id, message.from_user.id, "fa")
    updateObj = {
        '$set': {'lang': "fa"}
    }
    db.setUserFields(message.chat.id, message.from_user.id, updateObj)
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, "زبان بات فارسی انتخاب شد!", reply_markup=markup)


@bot.message_handler(commands=['table'])
def make_table(message):
    chat = db.getChat(message.chat.id)
    userIds = chat['users']
    usersThisChat = []
    for userId in userIds:
        usersThisChat.append(db.getUser(userId, userId))
    sortedUsers = sorted(usersThisChat, key=itemgetter('score'), reverse=True)
    row = 1
    msg_text = 'R  '+'Name'
    msg_text += '                 ' + 'Points\n' #24 spaces
    msg_text += '________________________\n'
    for user in sortedUsers:
        line_text = ''
        length = 0
        line_text += str(row) + '. '
        line_text += user['first'] + ' '
        length += len(user['first'])
        if user['last'] is not None:
            line_text += user['last']
            length += len(user['last'])
        if length < 30:
            for i in range(int(np.ceil(5/3*length)),30):
                line_text += ' '
        else:
            line_text += '\n'
            for i in range(30):
                line_text += ' '
        line_text += str(user['score'])
        row += 1
        msg_text += line_text + '\n'
    bot.send_message(message.chat.id, msg_text)





# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: message.chat.type == 'group')
def group_message(message):
    chatObj = db.getChat(message.chat.id)
    usersThisChat = chatObj['users']
    if "/ImIn" in message.text and message.from_user.id not in usersThisChat:
        usersThisChat.append(message.from_user.id)
        updateObj = {
            '$set': {'users': usersThisChat}
        }
        db.setChatField(message.chat.id, updateObj)
        chatObj = db.getChat(message.chat.id)
        bot.reply_to(message, """\
                    حالا به @WorldCup1818bot برو و /openbets را وارد کن.

Now let's go to @WorldCup1818bot and enter /openbets.
                    \
                    """)
    elif 'WorldCup1818bot' in message.text:
        bot.reply_to(message, 'Let\'s continue in private @WorldCup1818bot!')
    if usersThisChat == []:
        bot.send_message(message.chat.id,"""\
        برای پیش‌بینی نتایج بازی‌های جام‌جهانی به @WorldCup1818bot رفته و برای رقابت با دیگر اعضای گروه /ImIn را فشار دهید.

To Participate in WorldCup2018 Prediction Contest, Join @WorldCup1818bot and Press /ImIn here.
        \
        """)
    userObj = db.getUser(message.chat.id, message.from_user.id)


@bot.message_handler(func=lambda message: message.chat.type == 'supergroup')
def group_message(message):
    chatObj = db.getChat(message.chat.id)
    usersThisChat = chatObj['users']
    if usersThisChat == []:
        bot.send_message(message.chat.id,"""\
        برای پیش‌بینی نتایج بازی‌های جام‌جهانی به @WorldCup1818bot رفته و برای رقابت با دیگر اعضای گروه /ImIn را فشار دهید.

To Participate in WorldCup2018 Prediction Contest, Join @WorldCup1818bot and Press /ImIn here.
        \
        """)
    if '/ImIn' in message.text and message.from_user.id not in usersThisChat:
        usersThisChat.append(message.from_user.id)
        updateObj = {
            '$set': {'users': usersThisChat}
        }
        db.setChatField(message.chat.id, updateObj)
        chatObj = db.getChat(message.chat.id)
        bot.reply_to(message, """\
            حالا به @WorlCup1818bot برو و /openbets را وارد کن.
            
Now let's go to @WorldCup1818bot and enter /openbets.
            \
            """)
    elif 'WorldCup1818bot' in message.text:
        bot.reply_to(message, 'Let\'s continue in private @WorldCup1818bot!')
    userObj = db.getUser(message.chat.id, message.from_user.id)


@bot.message_handler(commands=['mypoints'])
def my_points(message):
    userId = message.from_user.id
    user = db.getUser(userId, userId)
    msg_text = 'شما تا اینجا '
    msg_text += str(user['score'])
    msg_text += ' امتیاز کسب کرده‌اید.'
    bot.reply_to(message,msg_text)


@bot.message_handler(func=lambda message: True)
def bet_time(message):
    userObj = db.getUser(message.chat.id, message.from_user.id)
    thisUserId = message.from_user.id
    thisChatId = message.chat.id
    if userObj['first'] == []:
        updateObj = {
            '$set': {'first': message.from_user.first_name}
        }
        db.setUserFields(thisChatId, thisUserId, updateObj)

    if userObj['last'] == []:
        updateObj = {
            '$set': {'last': message.from_user.last_name}
        }
        db.setUserFields(thisChatId, thisUserId, updateObj)

    # lang = db.getLang(message.chat.id, message.from_user.id)
    if 'updategame' not in message.text and 'sendreminder' not in message.text:
        if '-' in message.text:
            matches = db.loadOpenMatches()
            for m in matches:
                if m['flags'] == message.text:
                    updateObj = {
                        '$set': {'toBetMatchId': m['matchId']}
                    }
                    db.setUserFields(thisChatId, thisUserId, updateObj)
            show_bets(message)
        elif ':' in message.text:
            matches = db.loadOpenMatches()
            matchId = userObj['toBetMatchId']
            bets = userObj['bets']

            betValue = message.text

            isNewBet = True
            for i in range(len(bets)):
                if bets[i]['matchId'] == matchId:
                    bets[i]['value'] = betValue
                    isNewBet = False
                    break
            if isNewBet:
                bets.append({
                    'matchId': matchId,
                    'value': betValue
                })

            updateObj = {
                '$set': {'bets': bets}
            }
            db.setUserFields(thisChatId, thisUserId, updateObj)

            openBets = []
            for match in matches:
                alreadyBet = False
                for bet in userObj['bets']:
                    if bet['matchId'] == match['matchId']:
                        alreadyBet = True
                        break
                if not alreadyBet:
                    openBets.append(match)
                    break

            if len(openBets) != 0:
                show_games(message)
            else:
                markup = types.ReplyKeyboardRemove(selective=False)
                bot.send_message(message.from_user.id, text="""\
                همه‌ی بازی‌ها را پیش‌بینی کردید! برای تغییر نتایج /changebet را انتخاب کنید.
                \
                """, reply_markup=markup)




    elif 'updategame' in message.text: #For Final Score only 'updategame' in text

        commandParts = message.text.split(' ')
        matchId = commandParts[1]
        matchObj = {
            'matchId': matchId,
            'result': commandParts[2],
            'flags': commandParts[3]
        }
        db.updateMatch(matchId, matchObj)
        db.updateUserScores()
        print(commandParts)
        if commandParts[2] == 'C':
            group_bets(matchId, commandParts[3])
        elif commandParts[2] != 'O':
            update_tot_scores()




    elif 'sendreminder' in message.text:

        openMatches = db.loadOpenMatches()
        commandParts = message.text.split(' ')
        msg_text = '\n پیش‌بینی بازی‌های زیر را فراموش نکنید: \n Remember to bet on the following games:\n \n'
        for match in openMatches:
            if match['matchId'] in commandParts:
                msg_text += match['flags']
                msg_text += '\n'
        msg_text +='\n پیش‌بینی با شروع هر بازی بسته خواهد شد. \n Bet will be closed as the game starts.'
        if commandParts[1] == 'a' or commandParts[1] == 'p':
            allUsers = db.loadAllUsers()
            for user in allUsers:
                markup = types.ReplyKeyboardRemove(selective=False)
                try:
                    bot.send_message(chat_id=user['userId'], text=msg_text + ' /openbets', reply_markup=markup)
                except:
                    pass
        if commandParts[1] == 'a' or commandParts[1] == 'g':
            allChats = db.loadAllChats()
            flag = 1
            for chat in allChats:
                if flag == 1:
                    msg_text += '\n برای مشاهده‌ی جدول گروه دستور '
                    msg_text += '/table '
                    msg_text += 'را اجرا کنید.'
                    flag = 0
                markup = types.ReplyKeyboardRemove(selective=False)
                try:
                    bot.send_message(chat_id=chat['chatId'], text=msg_text + ' @WorldCup1818bot', reply_markup=markup)
                except:
                    pass



def show_bets(message):
    userObj = db.getUser(message.chat.id, message.from_user.id)
    markup = types.ReplyKeyboardMarkup()
    itembtn00 = types.KeyboardButton('0:0')
    itembtn10 = types.KeyboardButton('1:0')
    itembtn20 = types.KeyboardButton('2:0')
    itembtn30 = types.KeyboardButton('3:0')
    itembtn01 = types.KeyboardButton('0:1')
    itembtn11 = types.KeyboardButton('1:1')
    itembtn21 = types.KeyboardButton('2:1')
    itembtn31 = types.KeyboardButton('3:1')
    itembtn02 = types.KeyboardButton('0:2')
    itembtn12 = types.KeyboardButton('1:2')
    itembtn22 = types.KeyboardButton('2:2')
    itembtn32 = types.KeyboardButton('3:2')
    itembtn03 = types.KeyboardButton('0:3')
    itembtn13 = types.KeyboardButton('1:3')
    itembtn23 = types.KeyboardButton('2:3')
    itembtn33 = types.KeyboardButton('3:3')
    markup.row(itembtn00, itembtn10, itembtn20, itembtn30)
    markup.row(itembtn01, itembtn11, itembtn21, itembtn31)
    markup.row(itembtn02, itembtn12, itembtn22, itembtn32)
    markup.row(itembtn03, itembtn13, itembtn23, itembtn33)
    if userObj['lang'] == "fa":
        bot.send_message(chat_id=message.chat.id, text="لطفاً نتیجه‌ی بازی را پیش‌بینی کنید. می‌توانید نتیجه‌ی دلخواه را دستی وارد کنید (م. 5:0):", reply_markup=markup)
    else:
        bot.send_message(chat_id=message.chat.id, text="Please predict the score. You can enter your customized score (Eg 5:0):", reply_markup=markup)


def group_bets(matchId, flags):
    allChats = db.loadAllChats()
    for chat in allChats:
        msg_text = 'ییش‌بینی‌ها برای بازی:'
        msg_text += '\nHere are the bets for the game:'
        msg_text += '\n\n' + flags + '\n\n'
        for userId in chat['users']:
            userObj = db.getUser(userId, userId)
            for bets in userObj['bets']:
                if bets['matchId'] == matchId:
                    thisUser = bot.get_chat(userId)
                    msg_text += thisUser.first_name
                    if thisUser.last_name is not None:
                        msg_text += ' ' + thisUser.last_name
                    msg_text += ' ' + bets['value'] + "\n"
        markup = types.ReplyKeyboardRemove(selective=False)
        try:
            bot.send_message(chat_id=chat['chatId'],
                             text=msg_text + '\nپیش‌بینی برای این بازی بسته شد. اگر پیش‌بینی شما در لیست نیست /ImIn را انتخاب کنید.', reply_markup=markup)
        except:
            pass


def update_tot_scores():
    allMatches = db.loadAllMatches()
    allUsers = db.loadAllUsers()
    for user in allUsers:
        thisUserBets = user['bets']
        score = 0
        for bet in thisUserBets:
            for match in allMatches:
                if match['result'] == 'O':
                    continue
                if bet['matchId'] == match['matchId']:
                    final = match['result'].split(':')
                    drawFinal = 0
                    if int(final[0]) == int(final[1]):
                        drawFinal = 1
                        winnerFinal = int(final[0])
                        loserFinal = int(final[0])
                    elif int(final[0]) > int(final[1]):
                        winnerFinal = int(final[0])
                        loserFinal = int(final[1])
                    else:
                        winnerFinal = int(final[1])
                        loserFinal = int(final[0])
                    userBet = bet['value'].split(':')
                    drawUser = 0
                    if int(userBet[0]) == int(userBet[1]):
                        drawUser = 1
                        winnerUser = int(userBet[0])
                        loserUser = int(userBet[0])
                    elif int(userBet[0]) > int(userBet[1]):
                        winnerUser = int(userBet[0])
                        loserUser = int(userBet[1])
                    else:
                        winnerUser = int(userBet[1])
                        loserUser = int(userBet[0])
                    if winnerUser == winnerFinal and loserUser==loserFinal:
                        score += 25
                    elif winnerUser == winnerFinal and loserUser!=loserFinal and drawUser-drawFinal==0:
                        score += 18
                    elif winnerUser-loserUser == winnerFinal-loserFinal:
                        score += 15
                    elif loserUser == loserFinal and winnerUser!=winnerFinal and drawUser-drawFinal==0:
                        score += 12
                    elif (int(userBet[0])-int(userBet[1]))*(int(final[0])-int(final[1]))>0:
                        score += 10
                    elif winnerUser == loserUser:
                        score += 4
        updateObj = {
            '$set': {'score': score}
        }
        db.setUserFields(user['userId'], user['userId'], updateObj)


bot.polling()
