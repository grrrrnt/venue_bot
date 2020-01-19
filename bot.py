import telebot
import time
import datetime
import json
import requests
import os.path
import glob
import logging
import sqlite3
#from database.db_handler import DBHandler
from telebot import types
from telebot import *
from io import StringIO
from util import *
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot_token = '813143053:AAHOr7bTW2oeijkTcDu5ffkpoQGd7yGfvzo'
print("-"*15)
print("Initialising Venue Booking Telegram Bot")
bot = telebot.TeleBot(bot_token)
print("Venue Booking Telegram Bot is now ready")
print("-"*15)
print("Waiting to receive Telegram messages...")
ts = time.time()

logging.basicConfig(filename=LOG_DIR+ 'TeleBot ' +str(datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')) + 'log.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
logging.info('============== Start =================')
logging.info(str('Time Started: ' + datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')))
logging.info('main: TeleBot Started')
logging.info('======================================')

# Global variable to store faculty and datetime information
global fullInfo
fullInfo = []

#Buttons
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.send_message(message.chat.id, "Hello User!")

        markup = InlineKeyboardMarkup()
        markup.row_width = 3
        markup.add(InlineKeyboardButton("FASS", callback_data="cb_fass"), InlineKeyboardButton("BIZ", callback_data="cb_biz"), InlineKeyboardButton("COM", callback_data="cb_com"),
                    InlineKeyboardButton("UTown", callback_data="cb_utown"), InlineKeyboardButton("Engineering", callback_data="cb_engine"), InlineKeyboardButton("Science", callback_data="cb_science"),
                    InlineKeyboardButton("SDE", callback_data="cb_sde"), InlineKeyboardButton("Yale", callback_data="cb_yale"), InlineKeyboardButton("YST", callback_data="cb_yst"))
        bot.send_message(message.chat.id, "Select the *location* of the room that you would like to book", reply_markup=markup, parse_mode='MarkdownV2')
        return markup
        
    except Exception as e:
        bot.reply_to(message, "There was a problem. Please try again.")
        print(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_fass":
        fullInfo.append("fass")
        bot.answer_callback_query(call.id, "FASS is selected.")
        bot.send_message(call.message.chat.id, "When do you need a room?\nKey in the date and time in this format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')

    if call.data == "cb_biz":
        fullInfo.append("biz")
        bot.answer_callback_query(call.id, "BIZ is selected.")
        bot.send_message(call.message.chat.id, "When do you need a room?\nKey in the date and time in this format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')

    if call.data == "cb_com":
        fullInfo.append("com")
        bot.answer_callback_query(call.id, "COM is selected.")
        bot.send_message(call.message.chat.id, "When do you need a room?\nKey in the date and time in this format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')

    if call.data == "cb_utown":
        fullInfo.append("utown")
        bot.answer_callback_query(call.id, "UTown is selected.")
        bot.send_message(call.message.chat.id, "When do you need a room?\nKey in the date and time in this format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')
    
    if call.data == "cb_engine":
        fullInfo.append("engine")
        bot.answer_callback_query(call.id, "Engineering is selected.")
        bot.send_message(call.message.chat.id, "When do you need a room?\nKey in the date and time in this format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')

    if call.data == "cb_science":
        fullInfo.append("science")
        bot.answer_callback_query(call.id, "Science is selected.")
        bot.send_message(call.message.chat.id, "When do you need a room?\nKey in the date and time in this format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')

    if call.data == "cb_sde":
        fullInfo.append("sde")
        bot.answer_callback_query(call.id, "SDE is selected.")
        bot.send_message(call.message.chat.id, "When do you need a room?\nKey in the date and time in this format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')

    if call.data == "cb_yale":
        fullInfo.append("yale")
        bot.answer_callback_query(call.id, "Yale is selected.")
        bot.send_message(call.message.chat.id, "When do you need a room?\nKey in the date and time in this format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')

    if call.data == "cb_yst":
        fullInfo.append("yst")
        bot.answer_callback_query(call.id, "YST is selected.")
        bot.send_message(call.message.chat.id, "When do you need a room?\nKey in the date and time in this format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    dateTimeLength = len(message.text.split(' ')) - 1
    if dateTimeLength == 3 :
        dateInfo = message.text.split(' ',3)[0]
        startTimeInfo = message.text.split(' ', 3)[1]
        endTimeInfo = message.text.split(' ', 3)[3]
        dateInfoLength = len(dateInfo.split('/')) - 1
        startTimeLength = len(startTimeInfo.split(':')) - 1
        endTimeLength = len(endTimeInfo.split(':')) - 1

        # Check validity of the date first
        if dateInfoLength == 2 :
            dayInfo = int(dateInfo.split('/',2)[0])
            monthInfo = int(dateInfo.split('/',2)[1])
            yearInfo = int(dateInfo.split('/',2)[2])
            # Initialise Boolean Values
            monthCorrect = None
            yearCorrect = None
            timeCorrect = None
            # Validify Date Input
            if monthInfo == 2 :
                if dayInfo > 0 and dayInfo <= 28 :
                    monthCorrect = True
            elif monthInfo == 1 or monthInfo == 3 or monthInfo == 5 or monthInfo == 7 or monthInfo == 8 or monthInfo == 10 or monthInfo == 12 :
                if dayInfo > 0 or dayInfo <= 31 :
                    monthCorrect = True
            elif monthInfo == 4 or monthInfo == 6 or monthInfo == 9 or monthInfo == 11 :
                if dayInfo > 0 or dayInfo <= 30 :
                    monthCorrect = True
            else :
                bot.send_message(message.chat.id, "Error occurred\nPlease ensure that you key in a *valid* date and time information", parse_mode='MarkdownV2')
            # Ensure that the date is not earlier than current date
            if yearInfo < 2020 :
                bot.send_message(message.chat.id, "Error occurred\nPlease ensure that you key in a *valid* date and time information", parse_mode='MarkdownV2')
            elif yearInfo == 2020 :
                if monthInfo == 1 :
                    if dayInfo < 19 :
                        bot.send_message(message.chat.id, "Error occurred\nPlease ensure that you key in a *valid* date and time information", parse_mode='MarkdownV2')
                else :
                    yearCorrect = True
            else : 
                yearCorrect = True

        # Check validity of time information
        if startTimeLength == 1 and endTimeLength == 1 :
            startHour = int(startTimeInfo.split(':')[0])
            startMin = int(startTimeInfo.split(':')[1])
            endHour = int(endTimeInfo.split(':')[0])
            endMin = int(endTimeInfo.split(':')[1])

            if startHour >= 0 and startHour <=23 and endHour >= 0 and endHour <= 23 :
                if startMin >= 0 and startMin <= 59 and endMin >= 0 and endMin <= 59 :
                    if endHour == startHour :
                        # make sure that the end time is not earlier than start time
                        if endMin > startMin :
                            timeCorrect = True
                        else :
                            bot.send_message(message.chat.id, "Error occurred\nPlease ensure that your start time is *earlier* than your end time", parse_mode='MarkdownV2')
                    elif endHour > startHour :
                        timeCorrect = True
                    else :
                        bot.send_message(message.chat.id, "Error occurred\nPlease ensure that your start time is *earlier* than your end time", parse_mode='MarkdownV2')

        # Store date information into array if the datetime info is valid
        if yearCorrect == True and monthCorrect == True and timeCorrect == True :
            fullInfo.append(dateInfo)
            fullInfo.append(startTimeInfo)
            fullInfo.append(endTimeInfo)

    else :
        bot.send_message(message.chat.id, "Error occurred\nPlease ensure that you key in the date and time information in the correct format:\n*DD/MM/YYYY HH:MM to HH:MM*", parse_mode='MarkdownV2')

bot.polling() #gets bot to start listening for updates

#Handle error of non-integer time input