from motor.motor_tornado import MotorClient

# uri = "mongodb+srv://reivanstr:admin@test.dz1tzyu.mongodb.net/?retryWrites=true&w=majority&appName=Test"

# db = MotorClient(uri)['Main_Storage']
from motor.motor_tornado import MotorClient
db = MotorClient("mongodb+srv://reivanstr:admin@test.dz1tzyu.mongodb.net/?retryWrites=true&w=majority&appName=Test")["CKM_Storage"]
