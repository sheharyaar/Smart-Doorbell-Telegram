import RPi.GPIO as GPIO
import time
from time import sleep
from time import localtime,strftime
import random
import telepot
import os
import sys
import threading
from os import listdir
from os.path import isfile, join
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

#GPIO Pin Numbers
buzzer = 23
button = 27
buzzTime = 1
#Setting up Telepot
chat_id = '#Your Chat ID here'
bot = telepot.Bot('#Your BOT Token here')

# Function in initialise GPIO
def init():
    GPIO.setmode(GPIO.BCM)
    #Setup GPIO Pins
    GPIO.setup(button,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buzzer,GPIO.OUT)
    print("Bot is ONLINE!!!")

# Function to process image snapping
def snap():
    #Initialising names of folders and image by time
    raw_time = localtime()
    date_string = strftime("%d %b %Y, %a",raw_time)
    time_string = strftime("%I:%M %p")
    folder_name = strftime("%Y%m%d",raw_time) 
    file_name = strftime("%Y%m%d%H%M%S",raw_time)

    # Creating Folder directory for images to be saved 
    dir = os.getcwd()
    dir = dir + "/snaps/" + folder_name
    if(not os.path.exists(dir)):
        os.mkdir(dir)
    file_location = dir + "/" + file_name + ".jpg"
    
    #Clicking Pic and sending image
    print("-----------------------------------------------------------------------------------")
    print("Camera(fswebcam) log : ")
    command = "fswebcam -D 3 -S 10 --set brightness=50% --set contrast=20%  -F 5 -r  1280x720 --no-banner " + file_location
    os.system(command)
    message = "Alert someone is at your door.\nDay : "+date_string+"\nTime : "+time_string
    bot.sendMessage(chat_id,message)
    bot.sendPhoto(chat_id,open(file_location,'rb'))
    print("Sent the message")
    print("-----------------------------------------------------------------------------------")

# Buzzer function   
def buzz():
    GPIO.output(buzzer,True)
    sleep(buzzTime)
    GPIO.output(buzzer,False)

# Function to handle chat messages from user to Bot
def on_chat_message(msg):
    req = msg['text']
    print(f"Got request : {req}")
    req = req.replace('-','')       # stripping '-' for multipleDate input

    #Processing the numeric request.
    if req.isnumeric():
        print("got a numeric")
        if checkValidity(req) :
            getData(req)
        else : 
            bot.sendMessage(chat_id,text="Invalid date format please send again !\n")

    #Processing other requests
    else:
        if req == "/start":
            pass
        elif req == "/help":
            message = "Available Commands :\n"
            message += "1. /getdata : To retrieve the images capture on a day or a given duration of time."
            bot.sendMessage(chat_id,message)
        elif req == "/getdata":
            #date = findDate()
            message = "Data on your storage is available from the date : " #+ date + "\n" 
            message += "Select an option :"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                       [InlineKeyboardButton(text='1. Get Data of a given date.', callback_data='singleDate')],
                       [InlineKeyboardButton(text='2. Get Data using start and end date.', callback_data='multipleDate')]
                   ])
            bot.sendMessage(chat_id,message,reply_markup=keyboard)
        else:
            message = "Invalid command. Please type '/help' for help."
            bot.sendMessage(chat_id,message)

# Callback function for query buttons
def on_callback(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    
    if query_data == "singleDate":
        message = "Send the Date in DDMMYYYY format\n"
        bot.sendMessage(chat_id, message)
    if query_data == "multipleDate":
        message = "Send in 'startDate - endDate' format:\n"
        message += "ddMMyyyy - ddMMyyyy\n"
        bot.sendMessage(chat_id, message)

# To check if the given dates are in valid formats
def checkValidity(data):
    length = len(data)
    if length==8 or length==16:
        return True
    else:
        return False

# Function to manage getting the data from Pi
def getData(data):
    #First check if date valid or not
    length = len(data)
    if length == 8:
        data = filterData(data)
        data = int(data)
        sendData(data,data)
    elif length == 16:
        data1 = filterData(data[0:8])
        data1 = int(data1)
        data2 = filterData(data[8:16])
        data2 = int(data2)
        sendData(data1,data2)
    else:
        print("Some error ocurred in getData function!")  

# Function to process the sending of Data
def sendData(data1,data2):
    counter = 0;
    for i in range(data1,data2+1):
        dir = os.getcwd()
        dir = dir + "/snaps/"
        dir = dir + str(i)
        folder = str(i)
        if os.path.exists(dir):
            counter+=1
            files = [f for f in listdir(dir) if isfile(join(dir, f))]
            message = "Date : " + folder[6:8] + "-" + folder[4:6] + "-" + folder[0:4] + "\n"
            message += "Found [" + str(len(files)) + "] results."
            bot.sendMessage(chat_id,message)
            for f in files:
                message2 = "Time - " + f[8:10] + " : " + f[10:12] + " : " + f[12:14]
                bot.sendMessage(chat_id,message2)
                file_location = dir + "/" + f
                bot.sendPhoto(chat_id,open(file_location,'rb'))

    message = "Found (" + str(counter) + ") Dates.\n"
    bot.sendMessage(chat_id,message)    


# Formatting the received numeric data to match format of folders
def filterData(text):
    text = text[4:8] + text[2:4] + text[0:2]
    return text

# Main function
def main():
    #Call initialising function
    init()
    try:
        #Initialising Telepot msg handler which runs as a new thread
        MessageLoop(bot,{'chat': on_chat_message,'callback_query': on_callback}).run_as_thread()
        print("Bot is listening") 
        while True:
            state = GPIO.input(button)
            GPIO.output(buzzer,False)
            if state == False:
                #Calling buzz function as another thread
                thread1 = threading.Thread(target=buzz)
                thread1.start()
                snap()
                thread1.join()
            #sleep is important so that Pi does not get damaged due to infinite loop
            sleep(0.1)
            
    except Exception as e:
        print(e)
        
    finally:
        #Cleanup the GPIO pins for safety
        GPIO.output(buzzer,False)
        GPIO.cleanup()
        

# calling main function from here to prevent creating inifinite threads of infinite loops   
if __name__ == "__main__":
    main()

