from motor.motor_tornado import MotorClient
# from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://reivanstr:admin@test.dz1tzyu.mongodb.net/?retryWrites=true&w=majority&appName=Test"

db = MotorClient(uri, server_api = ServerApi('1'))['Storage']
