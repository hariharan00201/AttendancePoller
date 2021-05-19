import pymongo
from pymongo import MongoClient
from datetime import datetime

cluseter=MongoClient("mongodb+srv://hariharan:cricket20155@cluster0.0tdet.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db=cluseter["login_info"]


collection = db["users"]
collection1 = db["gallery"]
collection2 = db["profile"]
collection3 = db["schedules"]


def addPost(name,uname,dept,password,mail):
    post={"name" : name ,"uname" : uname , "dept" : dept , "pass" : password , "desig" : "s" , "mail" : mail}

    collection.insert_one(post)


def checkPost(uname,password):

    res=collection.find({"uname" : uname , "pass" : password})

    temp = []
    for result in res :
        temp.append(result)

    if(res.count() == 1):
        return True,temp[0]["desig"]

    return False


def addImage(user , img):

    collection1.insert_one({"user" : user , "img" : img})


def receiveImage(user):

    res = collection1.find({"user" : user})

    temp = []

    for a in res :
        temp.append(a["img"])

    return temp

def getUserDetails(user):

    res = collection.find({"uname" : user})

    temp = []

    for a in res :
        temp.append(a)

    return temp


def uploadProfile(user , img) :
    print('uploading')
    collection2.insert_one({"user": user, "img": img})


def getDept(user):

    res = collection.find({"uname" : user})

    temp = []

    for result in res :
        temp.append(result["dept"])

    return temp[0]


def getSchedules(dept):

    res = collection3.find({"dept" : dept , "end" : {"$gt" : datetime.now().strftime("%H:%M:%S")}})

    temp = []

    for result in res:
        temp.append(result)

    return temp


def getScheduleById(id):

    res = collection3.find({"id" : id})
    temp = []

    for result in res:
        temp.append(result)

    return temp[0]

def getStaffSchedules(user):
    res = collection3.find({"uname": user, "end" : {"$gt" : datetime.now().strftime("%H:%M:%S")}})
    temp = []

    for result in res:
        temp.append(result)

    return temp

def addSchedule(uname,dept,sub,st,et):

    collection3.insert_one({"uname" : uname , "dept" : dept , "sub" : sub , "start" : st , "end" : et , "id" : collection3.count()+1})

def getMail(dept):
    res = collection.find({"dept" : dept})

    temp = []

    for result in res:
        temp.append(result)

    return temp
