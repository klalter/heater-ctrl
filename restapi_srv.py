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

broker="35.199.81.127"
client= paho.Client("gcp-restAPI-001")

app = Flask(__name__)
api = Api(app)

class brinq_down(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderBrinq/command/set","down")
        client.disconnect()
        
        
        return {'command': 'ok'}

class brinq_up(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderBrinq/command/set","up")
        client.disconnect()
        
        return {'command': 'ok'}

class brinq_neutral(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderBrinq/command/set","neutral")
        client.disconnect()
        
        return {'command': 'ok'}

class suiteA_down(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderMaster/command/set","down")
        client.disconnect()
        
        return {'command': 'ok'}

class suiteA_up(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderMaster/command/set","up")
        client.disconnect()
        
        return {'command': 'ok'}

class suiteA_neutral(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderMaster/command/set","neutral")
        client.disconnect()
        
        return {'command': 'ok'}
    
class suiteB_down(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderMeninas/command/set","down")
        client.disconnect()
        
        return {'command': 'ok'}

class suiteB_up(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderMeninas/command/set","up")
        client.disconnect()
        
        return {'command': 'ok'}

class suiteB_neutral(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderMeninas/command/set","neutral")
        client.disconnect()
        
        return {'command': 'ok'}
    
class suiteC_down(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderHospede/command/set","down")
        client.disconnect()
        
        return {'command': 'ok'}

class suiteC_up(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderHospede/command/set","up")
        client.disconnect()
        
        return {'command': 'ok'}

class suiteC_neutral(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225d74/blinderHospede/command/set","neutral")
        client.disconnect()
        
        return {'command': 'ok'}

 class heater_on(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225c6a/heater/switch/set","true")
        client.disconnect()
        
        return {'command': 'ok'}   

 class heater_off(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225c6a/heater/switch/set","false")
        client.disconnect()
        
        return {'command': 'ok'}

 class compress_on(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225c6a/compressor/switch/set","true")
        client.disconnect()
        
        return {'command': 'ok'}

 class compress_off(Resource):
    def get(self):
        
        client.connect(broker)
        client.publish("homie/2c3ae8225c6a/compressor/switch/set","false")
        client.disconnect()
        
        return {'command': 'ok'}


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

api.add_resource(compress_on,'/api/order/compress/on') # Compressor ON
api.add_resource(compress_off,'/api/order/compress/off') # Compressor OFF

api.add_resource(heater_on,'/api/order/heater/on') # Compressor ON
api.add_resource(heater_off,'/api/order/heater/off') # Compressor OFF

if __name__ == '__main__':
     app.run(
         host = '0.0.0.0',
         port=5002)
