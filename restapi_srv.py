from flask import Flask, request
from flask_restful import Resource, Api
import flask
import pymongo
import json
from pymongo import MongoClient
from json import dumps
from flask_jsonpify import jsonify
import time
from time import strftime, localtime
from mongoqueue import MongoQueue

client = MongoClient('0.0.0.0', 27017)
db = client.boiler_DB

blinderdb = client.blinderdb
blinder_cmd = blinderdb.blinder_cmd


queue = MongoQueue(
    blinder_cmd,
    consumer_id="consumer-1",
    timeout=300,
    max_attempts=3)


status = db.status
history = db.history

app = Flask(__name__)
api = Api(app)


def online_offline():
    #Function to check if connectvitivy between raspberry and DB in cloud
    db = client.boiler_DB

    for t in db.heartbeat.find().sort([("_id", pymongo.DESCENDING)]).limit(1):
        if ((time.time()-t['heartbeat'])>15):
            return "Offline"
        else:
            return "Online"


class Status(Resource):
    def get(self):
        last_entry = status.find().sort([("_id", pymongo.DESCENDING)]).limit(1)
        for t in last_entry:
            json_status = t
            return {'currentState': json_status['res_actual'],'connection':json_status['connect'],'source':json_status['source'],'timestamp':json_status['timestamp']}

class history(Resource):
    def get(self):
        last_10_reg = db.history.find().sort([("_id", pymongo.DESCENDING)]).limit(1)
        for t in last_10_reg:
            json_status = t
            return flask.json.JSONEncoder(t)

class on(Resource):
    def get(self):
        post = {
            "res_actual":1,
            "timestamp":(strftime("%d-%m-%Y %H:%M:%S", localtime())),
            "source":'api',
            "connect":online_offline()
        }
        post_id = status.insert(post)
        return {'command': 'on'}

class off(Resource):
    def get(self):
        post = {
            "res_actual":0,
            "timestamp":(strftime("%d-%m-%Y %H:%M:%S", localtime())),
            "source":'api',
            "connect":online_offline()
        }
        post_id = status.insert(post)
        return {'command': 'off'}

class command(Resource):
    def post(self):
        if request.is_json:
            data = request.get_json()
            post = {
                "res_actual":data['targetState'],
                "timestamp":(strftime("%d-%m-%Y %H:%M:%S", localtime())),
                "source":'api',
                "connect":online_offline()
            }
            post_id = status.insert_one(post).inserted_id
            return jsonify(data)
        else:
            return jsonify(status="Request was not JSON")

class temperature(Resource):
    def get(self):
        last_entry = db.history.find().sort([("_id", pymongo.DESCENDING)]).limit(1)
        for t in last_entry:
            json_status = t
            return {'heaterTemperature': json_status['tempc_avg']}

class brinq_down(Resource):
    def get(self):
        queue.put({"command": "brinq_down"}) # add a job to queue
        return {'command': 'ok'}

class brinq_up(Resource):
    def get(self):
        queue.put({"command": "brinq_up"}) # add a job to queue
        return {'command': 'ok'}

class brinq_neutral(Resource):
    def get(self):
        queue.put({"command": "brinq_neutral"}) # add a job to queue
        return {'command': 'ok'}

class suiteA_down(Resource):
    def get(self):
        queue.put({"command": "suiteA_down"}) # add a job to queue
        return {'command': 'ok'}

class suiteA_up(Resource):
    def get(self):
        queue.put({"command": "suiteA_up"}) # add a job to queue
        return {'command': 'ok'}

class suiteA_neutral(Resource):
    def get(self):
        queue.put({"command": "suiteA_neutral"}) # add a job to queue
        return {'command': 'ok'}

class suiteB_down(Resource):
    def get(self):
        queue.put({"command": "suiteB_down"}) # add a job to queue
        return {'command': 'ok'}

class suiteB_up(Resource):
    def get(self):
        queue.put({"command": "suiteB_up"}) # add a job to queue
        return {'command': 'ok'}

class suiteB_neutral(Resource):
    def get(self):
        queue.put({"command": "suiteB_neutral"}) # add a job to queue
        return {'command': 'ok'}

class suiteC_down(Resource):
    def get(self):
        queue.put({"command": "suiteC_down"}) # add a job to queue
        return {'command': 'ok'}

class suiteC_up(Resource):
    def get(self):
        queue.put({"command": "suiteC_up"}) # add a job to queue
        return {'command': 'ok'}

class suiteC_neutral(Resource):
    def get(self):
        queue.put({"command": "suiteC_neutral"}) # add a job to queue
        return {'command': 'ok'}


api.add_resource(Status, '/api/status') # Route_1
api.add_resource(history, '/api/history') # Route_2
api.add_resource(command, '/api/order') # Route_3
api.add_resource(on,'/api/order/on') # Route_4
api.add_resource(off,'/api/order/off') # Route_5
api.add_resource(temperature,'/api/temperature') # Route_6

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

if __name__ == '__main__':
     app.run(
         host = '0.0.0.0',
         port=5002)
