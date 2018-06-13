# coding=utf-8
# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
import numpy as np
from telebot import types
import xlwt
import xlrd
import pymongo
from xlutils.copy import copy
import db
import os

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_TOKEN = os.environ['TELEGRAM_TOKEN']
# API_TOKEN = "602234037:AAEnaoUclYiYF_7E7mP3zerwxWDX2Ldrw_E"
# API_TOKEN = "450979982:AAEymX_wZh5kX1JD1-Ekb0CrF_xdCl-4LEQ"

bot = telebot.TeleBot(API_TOKEN)

logger.info("TG bot ready (API key: {})!".API_TOKEN)

rb = xlrd.open_workbook('WorldCupExcel.xls')
wb = copy(rb)
w_sheet = wb.get_sheet(0)

cnt = 0
user_id = []
group_id = []
group_user = [[0]]
language = ["fa"]
N = 4 #Number of Games
bets = [[0 for x in range(N)]]
games_to_bet = [[1 for x in range(N)]]
points = [[0 for x in range(N)]]
games = ['🇷🇺 - 🇸🇦', '🇪🇬 - 🇺🇾', '🇮🇷 - 🇲🇦', '🇪🇸 - 🇵🇹']
final_scores = [-1]
total_score = [0]
bet_game = 0
admin_mode = 0



class Player:
    def __init__(self, chat_id, first, last, groups, games, bets, total):
        self.chat_id = chat_id
        self.first = first
        self.last = last
        self.groups = []
        self.games = [1, 2]
        self.bets = []
        self.total = total


players = [Player(0, 0, 0, 0, 0, [1, 2], 0)]


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
    print(userObj)
    if message.from_user.id not in user_id:
        user_id.append(message.from_user.id)
        w_sheet.write(len(user_id), 0, message.from_user.id)
        bets.append([0 for x in range(N)])
        games_to_bet.append([0 for x in range(N)])
        points.append([0 for x in range(N)])
        print(user_id)
        wb.save('WorldCupExcel.xls')


@bot.message_handler(commands=['help'])
def instructions(message):
    ind = user_id.index(message.from_user.id)
    if language[ind] == 1:
        bot.reply_to(message, """\
        شما با انتخاب /openbets می‌توانید پیش‌بینی بازی‌هایی که هنوز پیش‌بینی نکرده‌اید را انجام دهید.
        
اگر نتیجه‌ی موردنظرتان در گزینه‌ها نبود، باید نتیجه را به صورت دستی با همان فرمت سایر نتایج وارد کنید. (اعداد به انگلیسی و جدا کردن به وسیله‌ی دونقطه)
        
نحوه‌ی امتیازدهی
در مرحله‌ی گروهی برای پیش‌بینی درست نتیجه، پیش‌بینی درست اختلاف و پیش‌بینی درست برنده به ترتیب ۱۰، ۷ و ۵ امتیاز است. (اگر بازی‌ای که مساوی پیش‌بینی کرده‌اید با نتیجه‌ای متفاوت مساوی شود ۷ امتیاز کسب می‌کنی
این امتیاز‌ها برای مرحله‌ی یک‌‌شانزدهم ۲۰، ۱۴ و ۱۰ خواهد بود. (گزینه‌ی مساوی در ۹۰ دقیقه و برنده‌ی نهایی اضافه خواهد شد.)
این امتیاز‌ها برای مرحله‌ی یک‌‌هشتم ۳۰، ۲۱ و ۱۵ خواهد بود.
این امتیاز‌ها برای مرحله‌ی یک‌‌چهارم ۴۰، ۲۸ و ۲۰ خواهد بود.
این امتیاز‌ها برای مرحله‌ی نیمه‌نهایی ۵۰، ۳۵ و ۲۵ خواهد بود.
این امتیاز‌ها برای مرحله‌ی نهایی ۶۰، ۴۲ و ۳۰ خواهد بود.
        \
        """)
    else:
        bot.reply_to(message, """\

        \
        """)



@bot.message_handler(commands=['bet'])
def revise_bet(message):
    ind = user_id.index(message.from_user.id)
    games_to_bet[ind] = [1 for x in range(N)]
    show_games(message)


@bot.message_handler(commands=['openbets', 'changebet'])
def show_games(message):
    markup = types.ReplyKeyboardMarkup()
    userObj = db.getUser(message.chat.id, message.from_user.id)
    if message.text == '/openbets':
        wantToHaveNewBet = True
        wantToChangeBet = False
    else:
        wantToHaveNewBet = False
        wantToChangeBet = True
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

    for Obet in openBets:
        itembtn1 = Obet['flags']
        markup.row(itembtn1)
    bot.send_message(chat_id=message.from_user.id, text= """\
    لطفاً بازی‌ موردنظر برای پیش‌بینی را انتخاب کنید:
    Please choose the game you want to bet on:
    \
    """, reply_markup=markup)


@bot.message_handler(commands=['ImIn@WorldCup1818bot'])
def ImIn(message):
    ind = group_id.index(message.chat.id)
    if message.from_user.id not in group_user[ind]:
        group_user[ind].append(message.from_user.id)


@bot.message_handler(commands=['language'])
def choose_language(message):
    markup = types.ReplyKeyboardMarkup()
    itembtnfar = types.KeyboardButton('فارسی')
    itembtneng = types.KeyboardButton('English')
    markup.row(itembtnfar, itembtneng)
    bot.send_message(chat_id=message.chat.id, text="Please choose your preferred language:", reply_markup=markup)


@bot.message_handler(commands=['english'])
def set_language(message):
    db.setLang(message.from_user.id, message.from_user.id, "en")
    if message.chat.type == 'private':
        ind = user_id.index(message.from_user.id)
        language[ind] = "en"
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.from_user.id, "You chose English!", reply_markup=markup)
        send_welcome_english(message.from_user.id)


@bot.message_handler(func=lambda message: message.text == 'فارسی')
def set_language(message):
    db.setLang(message.from_user.id, message.from_user.id, "fa")
    if message.chat.type == 'private':
        ind = user_id.index(message.from_user.id)
        language[ind] = "fa"
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.from_user.id, "زبان فارسی انتخاب شد!", reply_markup=markup)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: message.chat.type == 'group')
def group_message(message):
    #print(message.text)
    if message.chat.id not in group_id:
        group_id.append(message.chat.id)
        group_user.append([0])
        bot.send_message(chat_id=message.chat.id, text="""\
                        To Participate in WorldCup2018 Prediction Contest, Join @WorldCup1818bot and Press /ImIn here.
                        \
                        """)
        print(group_id)
    if message.text == '/ImIn@WorldCup1818bot':
        ind = group_id.index(message.chat.id)
        if group_user[ind][0] == 0:
            group_user[ind][0] = message.from_user.id
        fir = message.from_user.first_name
        if message.from_user.id not in group_user[ind]:
            group_user[ind].append(message.from_user.id)
            if message.from_user.id not in user_id:
                msg_txt = "Dear " + fir + "! Please Join @WorldCup1818bot and Press Start."
        else:
            msg_txt = 'Dear ' + fir + '! You Are Registered Already, Please Remember to Bet.'
        bot.send_message(chat_id=message.chat.id, text=msg_txt)
        print(group_user)


@bot.message_handler(commands=['table'])
def make_table(message):
    if message.chat.type == 'group':
        group_id = message.chat.id




@bot.message_handler(func=lambda message: True)
def bet_time(message):
    userObj = db.getUser(message.chat.id, message.from_user.id)
    print(userObj)
    thisUserId = message.from_user.id
    thisChatId = message.chat.id

    print('here1')
    lang = db.getLang(message.chat.id, message.from_user.id)
    print('here')
    print(lang)

    if 'updategame' not in message.text:
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
    elif 'farbod' not in message.text: #For Final Score only 'updategame' in text

        commandParts = message.text.split(' ')
        print(commandParts)
        matchId = commandParts[1]
        matchObj = {
            'matchId': matchId,
            'result': commandParts[2],
            'flags': commandParts[3]
        }
        db.updateMatch(matchId, matchObj)
        db.updateUserScores()
        # game_score = int(message.text[0:2])
        # print(game_score)
        # # final_scores[game_score]="message.text[2]:message.text[3]"
        # final_home = int(message.text[2])
        # print("final_home " + str(final_home))
        # final_away = int(message.text[3])
        # print("final_away " + str(final_away))
        # print(len(user_id))
        # for i in range(len(user_id)):
        #     bet_temp = bets[i][game_score]
        #     home = int(bet_temp[0])
        #     print("home " + str(home))
        #     away = int(bet_temp[2])
        #     print("away " + str(away))
        #     if home == final_home & away == final_away:
        #         total_score[i] = total_score[i] + 10
        #     elif home-away == final_home - final_away:
        #         total_score[i] = total_score[i] + 7
        #     elif (home-away)*(final_home-final_away) > 0:
        #         total_score[i] = total_score[i] + 5
        # print(total_score)
        admin_mode = 0
    else:
        game_close = int(message.text[0:2])
        print("Here are the bets for" + games[game_close] + "\n")
        print(group_id)
        for i in range(len(group_id)):
            print(group_id[i])
            for j in range(len(group_user[i])):
                chat_obj = bot.get_chat(group_user[i][j])
                print(chat_obj)
                fir = chat_obj.first_name
                if chat_obj.last_name != '':
                    las = chat_obj.last_name
                else:
                    las = ''
                print(fir + las)




def show_bets(message):
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
    bot.send_message(chat_id=message.chat.id, text="لطفاً نتیجه‌ی بازی را پیش‌بینی کنید:", reply_markup=markup)
    # bet = bot.get_updates()
    # print("bet is" + bet)


def send_welcome_english(userid):
    bot.send_message(userid, """\
    Hey, let see how well you can predict World Cup games!
    You can take a look at rules by pressing /help or start betting by pressing /openbets!
    \
    """)

bot.polling()
