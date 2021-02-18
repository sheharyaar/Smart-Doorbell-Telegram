import RPi.GPIO as GPIO
import time
from time import sleep
from time import localtime,strftime
import random
import telepot
import os
import sys
import threading

#GPIO Pin Numbers
buzzer = 23
button = 27
buzzTime = 0.2
#Setting up Telepot
chat_id = '714201444'
bot = telepot.Bot('1624782330:AAEsSFAxCSrQl7QBhnrvF1RRtEp9lejKn68')

def init():
    GPIO.setmode(GPIO.BCM)
    #Setup GPIO Pins
    GPIO.setup(button,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buzzer,GPIO.OUT)
    print("Bot is ONLINE!!!")


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
    
def buzz():
    GPIO.output(buzzer,True)
    sleep(buzzTime)
    GPIO.output(buzzer,False)

def main():
    #Call initialising function
    init()
    #GPIo waiting for input
    try:
        while True:
            state = GPIO.input(button)
            GPIO.output(buzzer,False)
            if state == False:
                #Calling buzz function at another thread
                thread1 = threading.Thread(target=buzz)
                thread1.start()
                snap()
                thread1.join()
            sleep(0.1)
            
    except Exception as e:
        print(e)
        
    finally:
        GPIO.output(buzzer,GPIO.LOW)
        GPIO.cleanup()
        
#calling main function
        
if __name__ == "__main__":
    main()

