from flask import Flask, request
from flask_restful import Resource, Api
import flask
import pymongo
import json
from json import dumps
from flask_jsonpify import jsonify
import time
from time import strftime, localtime
import paho.mqtt.client as paho


#####################
#JSON Objects
class jSONObj:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
class jSONPayLoad(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)
#####################  

#####################
#MQTT Section

broker="35.199.81.127"
device_id = "2c3ae8225c6a"

#broker="192.168.1.200"

heater = jSONObj();
compressor = jSONObj();


heater.status = "false";
heater.temperature = 0;
compressor.status = "false";

def on_message_heater_status(mosq, obj, msg):
    heater.status = str(msg.payload)
    print("HEATER STATUS: " + heater.status)

def on_message_heater_temp(mosq, obj, msg):
    temperature = json.loads(str(msg.payload))
    temperature = temperature['DS18B20']['Temperature']
    heater.temperature = temperature
    print("HEATER TEMPERATURE: " + str(heater.temperature))

def on_message_compressor(mosq, obj, msg):
    print("COMPRESSOR: " + str(msg.payload))
    compressor.status = str(msg.payload)

client= paho.Client("gcp-restAPI-001")

client.message_callback_add("homie/" + device_id + "/heater/switch", on_message_heater_status)
client.message_callback_add("homie/" + device_id + "/heater/degrees", on_message_heater_temp)
client.message_callback_add("homie/" + device_id + "/compressor/switch", on_message_compressor)

#####################

#####################
#FLASK App
app = Flask(__name__)
api = Api(app)

class brinq_down(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderBrinq/command/set","down")
        return {'command': 'ok'}

class brinq_up(Resource):
    def get(self):    
        client.publish("homie/" + device_id + "/blinderBrinq/command/set","up")
        return {'command': 'ok'}

class brinq_neutral(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderBrinq/command/set","neutral")
        return {'command': 'ok'}

class suiteA_down(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderMaster/command/set","down")
        return {'command': 'ok'}

class suiteA_up(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderMaster/command/set","up")
        return {'command': 'ok'}

class suiteA_neutral(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderMaster/command/set","neutral")
        return {'command': 'ok'}
    
class suiteB_down(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderMeninas/command/set","down")
        return {'command': 'ok'}

class suiteB_up(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderMeninas/command/set","up")
        return {'command': 'ok'}

class suiteB_neutral(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderMeninas/command/set","neutral")
        return {'command': 'ok'}
    
class suiteC_down(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderHospede/command/set","down")
        return {'command': 'ok'}

class suiteC_up(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderHospede/command/set","up")
        return {'command': 'ok'}

class suiteC_neutral(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/blinderHospede/command/set","neutral")
        return {'command': 'ok'}

class heater_on(Resource):
    def get(self): 
        client.publish("homie/" + device_id + "/heater/switch/set","true")
        return {'command': 'ok'}   

class heater_off(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/heater/switch/set","false")
        return {'command': 'ok'}

class heater_status(Resource):
    def get(self):
        return heater.toJSON()

class compress_on(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/compressor/switch/set","true")
        return {'command': 'ok'}

class compress_off(Resource):
    def get(self):
        client.publish("homie/" + device_id + "/compressor/switch/set","false")
        return {'command': 'ok'}
    
class compress_status(Resource):
    def get(self):
        return compressor.toJSON()


api.add_resource(brinq_down,'/api/order/blinder/brinq_down') # Blinder queue - Route_7
api.add_resource(brinq_up,'/api/order/blinder/brinq_up') # Blinder queue - Route_8
api.add_resource(brinq_neutral,'/api/order/blinder/brinq_neutral') # Blinder queue - Route_9

api.add_resource(suiteA_down,'/api/order/blinder/suiteA_down') # Blinder queue - Route_10
api.add_resource(suiteA_up,'/api/order/blinder/suiteA_up') # Blinder queue - Route_11
api.add_resource(suiteA_neutral,'/api/order/blinder/suiteA_neutral') # Blinder queue - Route_12

api.add_resource(suiteB_down,'/api/order/blinder/suiteB_down') # Blinder queue - Route_13
api.add_resource(suiteB_up,'/api/order/blinder/suiteB_up') # Blinder queue - Route_14
api.add_resource(suiteB_neutral,'/api/order/blinder/suiteB_neutral') # Blinder queue - Route_15

api.add_resource(suiteC_down,'/api/order/blinder/suiteC_down') # Blinder queue - Route_16
api.add_resource(suiteC_up,'/api/order/blinder/suiteC_up') # Blinder queue - Route_17
api.add_resource(suiteC_neutral,'/api/order/blinder/suiteC_neutral') # Blinder queue - Route_18

api.add_resource(compress_on,'/api/order/compressor/on') # Compressor ON
api.add_resource(compress_off,'/api/order/compressor/off') # Compressor OFF
api.add_resource(compress_status,'/api/order/compressor/status') # Status - ON or OFF

api.add_resource(heater_on,'/api/order/heater/on') # Compressor ON
api.add_resource(heater_off,'/api/order/heater/off') # Compressor OFF
api.add_resource(heater_status,'/api/order/heater/status') # Status - ON/OFF and Temperature
#####################

if __name__ == '__main__':
    client.connect(broker)
    client.subscribe("#", 0)
    client.loop_start()
    app.run(host = '0.0.0.0',port=5002)
