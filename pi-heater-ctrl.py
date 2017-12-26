# !/usr/bin/python
# -*- coding: utf-8 -*-
#

import spidev
import time
import math
import requests
import datetime
import forecast
import json
import struct
import thread
import pymongo
import sys, subprocess
from pymongo import MongoClient

from datetime import datetime
from time import gmtime, strftime, localtime

import RPi.GPIO as GPIO

from array import array

from time import sleep
import tm1637


#version control
version_c = "2.31"

#BCM Pin where heater is plugged
port_res = 2

#BCM Pin where AUTO led is plugged
port_led = 4

#BCM Pin where push button to turn-on-off heater is plugged
push_button = 3

#Temperature preset
temp_min = 32
temp_max = 60

#Reset target temperature
temp_target_enable = 0

#make temperatures global to be read in all functions.
global tempc
global tempc_avg
global internal_tempc


#GPIO pin-numbering scheme as BCM.
GPIO.setmode(GPIO.BCM)

#SET heater & led as out ports
GPIO.setup(port_res, GPIO.OUT)
GPIO.setup(port_led, GPIO.OUT)


#Prepare push button port to receive an interrupt. Also it enables the 10k pull_up resistor. In case of error (because the port is already set, it will pass.
try:
    GPIO.setup(push_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(push_button, GPIO.RISING,bouncetime=200)
except (RuntimeError):
    pass

# Initialize the display and set communication ports, CLK and DIO.
Display = tm1637.TM1637(CLK=21, DIO=20, brightness=1.0)

spi = spidev.SpiDev()
spi.open(0, 0)

tempc = float(0)

#Array of 240 float numbers to a good average.
tempc_array = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

sum_tempc = 0

#Variable that controls the history and post to stringfy.
count_update = 0

currentTemperature = 0
currentStatus = ''

force_warm = 1

def read_analog_temp(value,a,b,c,res):
    try:
        volts = (value * 3.3) / float(1023) + 0.0000000000000001
        ohms = (3.3/volts-1)*res #calculate the ohms of the thermististor
        lnohm = math.log1p(ohms) #take ln(ohms)
    except (ValueError):
        lnohm = 0
        pass

    #Steinhart Hart Equation
    #T = 1/(a + b[ln(ohm)] + c[ln(ohm)]^3)

    temp_int = 1/(a + b*lnohm + c*math.pow(lnohm,3)) #calcualte temperature

    temp_analog_convert = temp_int - 273.15 #K to C

    #print ("%4d/1023 V => %5.3f OHM => %5.3f TempC => %4.1f °C" % (value, volts, ohms, tempc))
    return temp_analog_convert

def open_database():
    #Open connection to boiler_DB (MongoDB)
    try:
        # replace 0.0.0.0 by the server IP.
        client = MongoClient('0.0.0.0',27017)
        db = client.boiler_DB
        return db
    except pymongo.errors.ConnectionFailure, e:
        print "%s : Could not connect to MongoDB = %s" % (strftime("%d-%m-%Y %H:%M:%S", localtime()),e)
        sys.exit("%s : Quitting" % (strftime("%d-%m-%Y %H:%M:%S", localtime())))


def run_updates():
    #log_history needs to be global. Exception function needs to close it.
    global log_history

    #Stringyfy URL info. To be used to prepare the JSON file.
    url = "https://webhooks.stringify.com/v1/events/fEKBTcS1iCb3F99yGsNpV9svvetMzGwG/1/283846e9793a1016a03c2459446af4ba/64GikL8RBDjpnBDDlOqf"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    #Make sure that the temperature will be stable
    #time.sleep(10)

    #Set JSON to send to stringyfy
    data = {'Key1' : tempc_avg,'Key2': res_actual}
    print data
    #Connect to Stringyfy
    r = requests.post(url, json=data, headers=headers)

    print "%s : Stringify update status code = %s" % (strftime("%d-%m-%Y %H:%M:%S", localtime()),r.status_code)

    #Set-up strings to log in file
    date_now = strftime("%d-%m-%Y %H:%M:%S", localtime())

    ############################## KEEP FOR NOW
    #Open History file
    log_history = open("/home/pi/boiler/history","a")
    ############################## KEEP FOR NOW

    #Get data from Dark Sky API
    weather_temp()

    #Prepare post for database
    post = {
        "date_now":date_now,
        "tempc_avg":tempc_avg,
        "currentTemperature":currentTemperature,
        "internal_tempc":internal_tempc,
        "currentStatus":currentStatus,
        "res_actual":res_actual
    }

    #instance a DB to open history collection
    db = open_database()
    history = db.history

    #insert post into the database
    post_id = history.insert_one(post).inserted_id

    print "%s : History database updated = %s" % (strftime("%d-%m-%Y %H:%M:%S", localtime()),post_id)


    ############################## KEEP FOR NOW
    #Log data to file
    log_history.write("%s         %f          %f          %f          %s          %s\n" % (date_now,tempc_avg, currentTemperature,internal_tempc,currentStatus,res_actual))
    log_history.close
    ############################## KEEP FOR NOW

def weather_temp():
    global currentTemperature
    global currentStatus
    query_url = "https://api.darksky.net/forecast/2c1ccc72aaa680eeebec239cab42ec95/-22.973710,-47.082462?units=si"
    rweather = requests.get(query_url)
    if rweather.status_code != 200:
        print "%s : Error getting data from Darksky, code = %s" % (strftime("%d-%m-%Y %H:%M:%S", rweather.status_code))
    json_weather = rweather.json()
    currentTemperature = json_weather['currently']['temperature']
    currentStatus = json_weather['currently']['summary']


def get_last_res_status():
    db = open_database()
    status = db.status
    last_entry = status.find().sort([("_id", pymongo.DESCENDING)]).limit(1)

    for t in last_entry:
        return t


def res_status(start):
    # control heater, On or Off based last status on database.
    global force_warm


    try:
        status_json = get_last_res_status()
        res = status_json['res_actual']

    except:
        res = 0;
        pass;

    if res == 0:
        GPIO.output(port_res, GPIO.LOW)
        if start == 1:
            print "%s : Heater is OFF" % strftime("%d-%m-%Y %H:%M:%S", localtime())
    elif res == 1:
        GPIO.output(port_res, GPIO.HIGH)
        if start == 1:
            print "%s : Heater is ON" % strftime("%d-%m-%Y %H:%M:%S", localtime())


    post = {
        "heartbeat":time.time()
    }

    # open database connection to print last time check. Used as heartbeat.
    db = open_database()
    heartbeat = db.heartbeat

    #insert post into the heartbeat
    post_id = heartbeat.insert_one(post).inserted_id

    return res

def set_off_force(currentT, maxT,res_actual):
    # force heater if temp max is reached
    global force_warm
    if currentT > maxT and res_actual==1:
        #Force mode is off and Auto is on.
        set_res_zero()
        force_warm = 0
        GPIO.output(port_led, GPIO.HIGH)
        print "%s : Boiler Temperature of %.2f C reached max defined temperature." % (strftime("%d-%m-%Y %H:%M:%S", localtime()),currentT)

def set_res_zero():
    db = open_database()
    status = db.status

    post = {
        "res_actual":0,
        "date_now":time.time(),
        "source":'pi'
    }
    post_id = status.insert_one(post).inserted_id


def show_display(tempc_avg):
    if tempc_avg  > 100:
        Display.Show1(0,9)
        Display.Show1(1,9)
        Display.Show1(2,9)
    elif tempc_avg < 0:
        Display.Show1(0,0)
        Display.Show1(1,0)
        Display.Show1(2,0)
    else:
        d1 = int(tempc_avg / 10)
        Display.Show1(0,d1)
        d2 = int(tempc_avg - d1*10)
        Display.Show1(1,d2)
        d3 = int((tempc_avg - d1*10 - d2)*10)
        Display.Show1(2,d3)

def set_warm_force(on_off):
    # turn on or off the heater based on button push or any other external data
    global force_warm

    #Toggle force warm variable
    if force_warm == 1:
        force_warm = 0
        GPIO.output(port_led, GPIO.HIGH)
        print "%s : Auto mode is ON" % (strftime("%d-%m-%Y %H:%M:%S"))
    elif force_warm ==0:
        GPIO.output(port_led, GPIO.LOW)
        force_warm = 1
        print "%s : Auto mode is OFF" % (strftime("%d-%m-%Y %H:%M:%S"))

    # IF force heater is on, them change RES status.
    if force_warm == 1:
        db = open_database()
        status = db.status

        if on_off == 1:
            #If heater already ON them TURN it OFF
            post = {
                "res_actual":0,
                "date_now":time.time(),
                "source":'pi'
            }
            post_id = status.insert_one(post).inserted_id
        elif on_off == 0:
            #IF heater already OFF them TURN it ON
            post = {
                "res_actual":1,
                "date_now":time.time(),
                "source":'pi'
            }
            post_id = status.insert_one(post).inserted_id

def set_warm_mintemp(actual_temp,min_temp):
# turn on or off the heater based on min temp and schedule
    global on_off_res
    global temp_target #variable to control the target temperature if the temperature is below the min, usually 4C above min.
    global temp_target_enable #variable to tell the target tempearure is enabled.

    temp_target = 4

    # reset temp target enable and return if buttom is pushed.
    if force_warm == 1:
        temp_target_enable = 0
        return

    db = open_database()
    status = db.status

    if temp_target_enable == 1:
        if actual_temp < (min_temp+temp_target):
            #below target temperature, heater needs to be on.
            post = {
                "res_actual":1,
                "date_now":time.time(),
                "source":'pi'
            }
            post_id = status.insert_one(post).inserted_id
            on_off_res = 1
        else:
            #Temperature reached the min + target temp.
            temp_target_enable = 0
            print "%s : Boiler Temperature of %.2f C above min (+%s) %.0f C" % (strftime("%d-%m-%Y %H:%M:%S", localtime()),actual_temp,temp_target,min_temp)
    else:
        if actual_temp < min_temp:
            #bellow min temperature, heater needs to be on.
            post = {
                "res_actual":1,
                "date_now":time.time(),
                "source":'pi'
            }
            post_id = status.insert_one(post).inserted_id
            on_off_res = 1
            on_off_res = 1
            temp_target_enable = 1
            print "%s : Boiler Temperature of %.2f C below min %.0f C" % (strftime("%d-%m-%Y %H:%M:%S", localtime()),actual_temp,min_temp)
        else:
            #Hot, heater needs to be off.
            post = {
                "res_actual":0,
                "date_now":time.time(),
                "source":'pi'
            }
            post_id = status.insert_one(post).inserted_id
            on_off_res = 1
            on_off_res = 0


    status_res.close()

def readadc(adcnum):
# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    adcout = ((r[1] & 3) << 8) + r[2]
    return adcout

def run_restapi_srv():
    subprocess.call( ["python", "./restapi_srv.py"] )

#Initializing status file and port status
print "%s : Starting boiler control v%s" % (strftime("%d-%m-%Y %H:%M:%S"),version_c)
set_warm_force(0)
res_status(1)
res_old = 0

sum_tempc = 0
i = 0

#command = './restapi_srv.py'
#thread.start_new_thread(run_restapi_srv, ())

#print "%s : RESTAPI Started on 192.168.1.200:5002" % (strftime("%d-%m-%Y %H:%M:%S"))

try:
    #Read and stabilize the temperature. Do in memory to increase speed.
    while i<240:
        tempc = read_analog_temp(readadc(0),0.0028614590759171235,-0.0000687198488641089,0.000001434809116467907
,10000)
        tempc_array[i] = tempc

        if tempc_array[i] < 0:
                tempc_array[i] = 0

        sum_tempc = sum_tempc + tempc_array[i]

        tempc_avg = sum_tempc / 240

        i = i+1

    #Get internal temp to start-up log
    internal_tempc = read_analog_temp(readadc(7),0.002197222470870,0.000161097632222,0.000000125008328,3300)
    #Print boiler temp to start-up log
    print "%s : Boiler Temperature %.2f C" % (strftime("%d-%m-%Y %H:%M:%S"), tempc_avg)
    #Print internal temp to start-up log
    print "%s : Internal Temperature %.2f C" % (strftime("%d-%m-%Y %H:%M:%S"), internal_tempc)

    while True:
        #Call read_analog_temp (value_adc, A-coeficient, B-coeficient, C-coeficient)
        tempc = read_analog_temp(readadc(0),0.0028614590759171235,-0.0000687198488641089,0.000001434809116467907
,10000)
        internal_tempc = read_analog_temp(readadc(7),0.002197222470870,0.000161097632222,0.000000125008328,3300)

        j = 0

        #Loop i from 1 to 30. To make the array to calculate the average, the last 10 reads are take into consideration.
        if i == 240:
            i = 0

        tempc_array[i] = tempc

        sum_tempc = 0

        while j < 240:
            if tempc_array[j] < 0:
                tempc_array[j] = 0

            sum_tempc = sum_tempc + tempc_array[j]
            j = j + 1

        tempc_avg = sum_tempc / 240

        i = i + 1

        #function to show temperature on display:
        show_display(tempc_avg)

        time.sleep(0.5)

        #get heater status based on value inside status file.
        res_actual = res_status(0)

        #Turn On of Off based on Min temperature & Forecast.
        #set_warm_mintemp(tempc_avg,temp_min)

        #Turn Off when max temperature defined is reached.
        #set_off_force(tempc,temp_max,res_actual)


        #Check if button is pushed or if the status file modified. It will change the AUTO mode, forcing heater to go off or on.
        if GPIO.event_detected(push_button):
            set_warm_force(res_actual)
            #Update heater actual status.
            #res_actual = res_status(1)
            #print "%s : PUSH" % strftime("%d-%m-%Y %H:%M:%S", localtime())

        #Log information if changes on heater status and change AUTO mode to disable.
        if res_actual <> res_old and res_actual == 1 :
            print "%s : Heater is ON" % strftime("%d-%m-%Y %H:%M:%S", localtime())
            GPIO.output(port_led, GPIO.LOW)
            force_warm = 1
            print "%s : Auto mode is OFF" % (strftime("%d-%m-%Y %H:%M:%S"))
        elif res_actual <> res_old and res_actual == 0:
            print "%s : Heater if OFF" % strftime("%d-%m-%Y %H:%M:%S", localtime())
            GPIO.output(port_led, GPIO.LOW)
            force_warm = 1
            print "%s : Auto mode is OFF" % (strftime("%d-%m-%Y %H:%M:%S"))

        res_old = res_actual

        count_update = count_update + 1
        #update stringyfy and history file every 150 seconds.
        if count_update >= 300:
            print "%s : Starting stringify & history updates" % strftime("%d-%m-%Y %H:%M:%S")
            thread.start_new_thread(run_updates, ())
            count_update = 0

        Display.Clear()

except (KeyboardInterrupt): # If CTRL+C is pressed, exit cleanly:
    Display.Clear()
    GPIO.output(port_res,GPIO.LOW)
    GPIO.output(port_led, GPIO.LOW)
    GPIO.remove_event_detect(push_button)
    log_history.close
    GPIO.cleanup() # cleanup all GPIO
    print "%s : Ending boiler control" % strftime("%d-%m-%Y %H:%M:%S")
