import telebot
import time
import datetime
import json
import requests
import os.path
import glob
import logging
import sqlite3
from database.db_handler import DBHandler
from telebot import types
from io import StringIO
from util import *


bot_token = '817233185:AAFHWV5-C9SBR-3BrGpUZGd78RJlvVGu8Y4'
print("-"*15)
print("Initialising Amaris AI Telegram API Bot")
bot = telebot.TeleBot(token=bot_token)
print("Amaris AI Telegram API Bot is now ready")
print("-"*15)
print("Waiting to receive Telegram messages...")
ts = time.time()

logging.basicConfig(filename=LOG_DIR+ 'TeleBot ' +str(datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')) + 'log.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
logging.info('============== Start =================')
logging.info(str('Time Started: ' + datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')))
logging.info('main: TeleBot Started')
logging.info('======================================')

#Buttons

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.send_message(message.chat.id, "Hello User!")
        bot.send_message(message.chat.id, "Send Your Job ID as: *JOB AXXX*", parse_mode='MarkdownV2')
    except Exception as e:
        bot.reply_to(message, "There was a problem. Please try again.")
        print(e)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_job":
        bot.answer_callback_query(call.id, "Confirm Job")
        bot.send_message(call.message.chat.id, "Send your Job ID as: JOB AXXX")

    if call.data == "cb_location":
        bot.answer_callback_query(call.id, "Please confirm your location.")
        markup = types.ReplyKeyboardMarkup(row_width = 1, one_time_keyboard = True, resize_keyboard = True)
        markup.add(types.KeyboardButton("Location", request_location = True))
        bot.send_message(call.message.chat.id, "Send Your Location", reply_markup=markup)

    if call.data == "cb_image":
        bot.answer_callback_query(call.id, "Please send in your image.")

def checkJobId(jobId):
    conn = sqlite3.connect("amaris_manhole.db")
    db_handler = DBHandler(conn)
    # db_handler.create_tables()
    coordinates = db_handler.get_job(jobId)
    # coordinates = db_handler.view_data("JobsTable", jobId)
    print(coordinates)
    return coordinates

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    keyword = message.text.split(' ',1)[0]
    if keyword == "JOB" :
        jobId = message.text.split(' ', 1)[1]
        # #Do something to check from database if correct ID
        coordinates = checkJobId(jobId)
        if coordinates == 'Job not found!':
            bot.send_message(message.chat.id, "Please check your Job ID and try again.")
        else:
            # latitude_str = coordinates.split(',')[0]
            # longitude_str = coordinates.split(',')[1]
            markup = types.ReplyKeyboardMarkup(row_width = 1, one_time_keyboard = True, resize_keyboard = True)
            markup.add(types.KeyboardButton("Location", request_location = True))
            bot.send_message(message.chat.id, "Send Your *Location*", reply_markup=markup, parse_mode='MarkdownV2')
            #Find a way to get telegram messages from the past to take JOB ID to read from database.
            #This is a temporary implementation
            f = open("tempCoord.txt", '+a')
            f.write(coordinates)
            f.close()

        saveMessageToFile(message)
        #else ask user to send again or reconfirm Job location 
    else :
        reply = saveMessageToFile(message) #saves the text to message_log.txt
        bot.reply_to(message,reply) #responds with success message

@bot.message_handler(content_types=['location'])
def handle_location(message):
        actual_lat = str(message.location.latitude)
        actual_long = str(message.location.longitude)
        bot.send_message(message.chat.id, "Latitude: " + actual_lat)
        bot.send_message(message.chat.id, "Longitude: " + actual_long)
        try:
            with open('tempCoord.txt', 'r') as file:
                coordinates = file.read().replace('\n', '')
            job_lat = float(coordinates.split(',')[0])
            job_long = float(coordinates.split(',')[1])
            os.remove('tempCoord.txt')
            print(str(float(actual_lat) - job_lat))

            if ((float(actual_lat) - job_lat < 0.0008) and (float(actual_lat) - job_lat > -0.0008)) and ((float(actual_long) - job_long < 0.0008) and (float(actual_long) - job_long > -0.0008)):
                bot.send_message(message.chat.id, "You are at the correct location.")
                bot.send_message(message.chat.id, "Please send in the *Duct Image*", parse_mode='MarkdownV2')
            else:
                bot.send_message(message.chat.id, "You are at the wrong location.")
        except Exception as e:
            bot.send_message(message.chat.id, 'There was a problem.')
            bot.send_message(message.chat.id, "*Have you input your Job Id?*", parse_mode='MarkdownV2')


@bot.message_handler(content_types=['photo'])
def handle_picture(message):

    savePictureToLogs(message) #saves the information of the document to document_log.txt
    reply = savePictureToFile(message) #saves the document to doc.[FILE_TYPE]
    bot.reply_to(message,reply) #responds with success message

@bot.message_handler(content_types=['document'])
def handle_doc(message):
    saveDocumentToLogs(message) #saves the information of the document to document_log.txt
    reply = saveDocumentToFile(message) #saves the document to doc.[FILE_TYPE]
    bot.reply_to(message,reply) #responds with success message

@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    reply = saveAudioDocToFile(message) #saves the document to doc.[FILE_TYPE]
    bot.reply_to(message,reply) #responds with success message

@bot.message_handler(content_types=['video'])
def handle_video(message):
    reply = saveVideoDocToFile(message) #saves the document to doc.[FILE_TYPE]
    bot.reply_to(message,reply) #responds with success message

def saveAudioDocToFile(msg):
    file_id = msg.audio.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    df = open("toTransfer/audio" + str(msg.message_id) + ".mp3","wb")
    logging.info('main: Created file at' + "toTransfer/audio" + str(msg.message_id) + ".mp3")
    df.write(downloaded_file) #saves the downloaded file into 'doc'.[FILE_TYPE]
    df.close()
    transfer()
    return "Your audio document has been saved successfully"

def saveVideoDocToFile(msg):
    file_id = msg.video.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    mime_type = msg.video.mime_type
    split_string = mime_type.split("/")
    file_type = split_string[1]
    df = open("toTransfer/video" + str(msg.message_id) + "." + file_type,"wb")
    logging.info('main: Created file at' + "toTransfer/video" + str(msg.message_id) + "." + file_type)
    df.write(downloaded_file) #saves the downloaded file into 'video'.[FILE_TYPE]
    df.close()
    transfer()
    return "Your video document has been saved succcessfully"

def saveMessageToFile(msg):
    f = open("toTransfer/message" + str(msg.message_id) + ".txt", "a+") #a+ signifies that this is an append operation
    if msg.chat.last_name is None : #checks if there is no last name field
        result = "Message ID :" + str(msg.message_id) + "|Chat ID :" + str(msg.chat.id) + "|Username :" + msg.chat.username + "|Name :" + msg.chat.first_name + "|Text : " + msg.text + "|\n"
        logging.info('main: ' + result)
    else :
        result = "Message ID :" + str(msg.message_id) + "|Chat ID :" + str(msg.chat.id) + "|Username :" + msg.chat.username + "|Name :" + msg.chat.first_name + " " + msg.chat.last_name + "|Text : " + msg.text + "|\n"
        logging.info('main: ' + result)
    finalresult = deEmojify(result) #removes emojis from the text message, deemed not necessary
    f.write(finalresult)
    f.close()
    transfer()
    return "Your message has been saved successfully"


def saveDocumentToFile(msg):
    file_id = msg.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path) #downloads the file sent to telegram bot
    split_string = (msg.document.file_name).split(".")
    file_type = split_string[1] #infers the file type from the name of the file
    df = open("toTransfer/" + str(msg.document.file_name), "wb")
    logging.info('main: Created file at' + "toTransfer/" + str(msg.message_id) + "." + file_type, "wb")
    df.write(downloaded_file) #saves the downloaded file into 'doc'.[FILE_TYPE]
    df.close()
    transfer()
    return "Your document has been saved successfully"

def saveDocumentToLogs(msg):
    f = open("document_log.txt", "a+") #a+ signifies that this is an append operation
    if msg.chat.last_name is None:
        result = "Message ID :" + str(msg.message_id) + "|Chat ID :" + str(msg.chat.id) + "|Username :" + msg.chat.username + "|Name :" + msg.chat.first_name + "|File Name : " + msg.document.file_name + "|\n"
        logging.info('main: ' + result)
    else :
        result = "Message ID :" + str(msg.message_id) + "|Chat ID :" + str(msg.chat.id) + "|Username :" + msg.chat.username + "|Name :" + msg.chat.first_name + " " + msg.chat.last_name +  "|File Name : " + msg.document.file_name + "|\n"
        logging.info('main: ' + result)
    f.write(result)
    f.close()

# def savePictureToFile(msg):
#     bot.reply_to(msg, "PROCESSING IMAGE...")
#     file_id = msg.photo[0].file_id
#     file_info = bot.get_file(file_id)
#     downloaded_file = bot.download_file(file_info.file_path) #downloads the file sent to telegram bot
#     PICTURE = "picture" + str(msg.message_id) + ".jpg"
#     df = open("toTransfer/picture" + str(msg.message_id) +".jpg", "wb")
#     logging.info('main: Created file at' + "toTransfer/picture" + str(msg.message_id) +".jpg")
#     df.write(downloaded_file) #saves the downloaded file into 'picture'.[FILE_TYPE]
#     df.close()
#     transfer()
#     #Handle Cable Duct Image Processing
#     cableDuctOut = subprocess.run(["python", "test.py", "testMoveDir/" + PICTURE], stdout = subprocess.PIPE)
#     cableDuctResult = str(cableDuctOut.stdout.decode()).rstrip()        
#     cableDuctPhoto = open('scriptImages/demo.png', 'rb')
#     cableNum = cableDuctResult.split(' ')[-1]
#     bot.send_photo(msg.chat.id, cableDuctPhoto)
#     bot.send_message(msg.chat.id, cableDuctResult)
#     os.remove('scriptImages/demo.png') #cleanup

#     #Handle Blueprint Processing
#     blueprintOut = subprocess.run(["python", "demoBlueprint.py"], stdout = subprocess.PIPE)
#     blueprintResult = str(blueprintOut.stdout.decode()).rstrip()
#     blueprintPhoto = open('scriptImages/blueprint_reference.png', 'rb')
#     blueNum = blueprintResult.split(' ')[-1]
#     bot.send_photo(msg.chat.id, blueprintPhoto)
#     if cableNum == blueNum:
#         return ("You have inserted the cable correctly into Duct " + cableNum + ". Good work!")
#         #bot.send_message(msg.chat.id, "You have inserted the cable correctly into duct " + cableNum + ". Good work :).")
#     else:
#         return ("According to the blueprint, the correct Duct is Duct " + blueNum + ". Please check and try again :).")
#         #bot.send_message(msg.chat.id, "According to the blueprint, the correct duct is " + blueNum + ". Please check and try again.")

    #transfers files stored in the toTransfer folder to MASTER drive/testMoveDir(if master drive is not found)
def transfer():
    moveDir = SearchMasterDrive()
    moveFolder(OUTPUT_DIR,moveDir)
    print("Transferring from: " + OUTPUT_DIR + " to " + moveDir)
    print("="*15)
    print("Waiting to receive Telegram messages...")
    logging.info('main: Transferring from: ' + OUTPUT_DIR + " to " + moveDir)
    logging.info('main: Waiting to receive Telegram messages...')
    logging.info("="*15)

def savePictureToLogs(msg):
    f = open("photo_log.txt", "a+") #a+ signifies that this is an append operation
    if msg.chat.last_name is None:
        result = "Message ID :" + str(msg.message_id) + "|Chat ID :" + str(msg.chat.id) + "|Username :" + msg.chat.username + "|Name :" + msg.chat.first_name + "|PHOTO " + "|\n"
        logging.info('main: ' + result)
    else :
        result = "Message ID :" + str(msg.message_id) + "|Chat ID :" + str(msg.chat.id) + "|Username :" + msg.chat.username + "|Name :" + msg.chat.first_name + " " + msg.chat.last_name +  "|PHOTO " + "|\n"
        logging.info('main: ' + result)
    f.write(result)
    f.close()
    return "Your photo has been saved successfully"

def saveEmojis(msg):
    f = open("emoji_log.txt", "a+")
    if msg.chat.last_name is None:
        result = "Message ID :" + str(msg.message_id) + "|Chat ID :" + str(msg.chat.id) + "|Username :"
        logging.info('main: ' + result)

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

def extractQuotes(inputString):
    return inputString.split("'")[1]


bot.polling() #gets bot to start listening for updates


