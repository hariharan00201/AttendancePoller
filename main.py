import json
import smtplib
import threading
import pandas as pd
from cv2.dnn import readNet
from datetime import datetime
import datasource
from camera import VideoCamera
from flask import Flask,render_template,request,jsonify,Response,redirect,url_for,session,copy_current_request_context
from flask_socketio import SocketIO,emit,disconnect
from threading import Lock
import base64
from flask_pymongo import PyMongo

app = Flask(__name__)
async_mode = None
app.config['SECRET_KEY'] = 'secret!'
socket_ = SocketIO(app, async_mode=async_mode, always_connect=True, engineio_logger=True)
thread = None
thread_lock = Lock()
user_list = {}
app.config['MONGO_URI'] = "mongodb+srv://hariharan:cricket20155@cluster0.0tdet.mongodb.net/login_info?retryWrites=true&w=majority"
mongo = PyMongo(app)
vid = None
dept = {"it" : "Information Technology" ,
        "ct" : "Computer Technology" ,
        "ae" : "Automobile Engineering",
        "ie" : "Instrumentation Enginerring"
        }

class user :

    def __init__(self,unam,vidca):
        self.uname = unam
        self.vidcam = vidca


@app.route('/')
def message():
    return render_template("home.html")


@app.route("/home/login")
def login():
    print('login')
    return render_template("login.html")

@app.route("/home/<user>/login")
def user_login(user):
    print('login')
    return redirect(url_for('login'))



@app.route("/home/signin")
def signin():
    return render_template("signin.html")


@app.route("/home/<user>/signin")
def user_signin(user):
    return redirect(url_for("signin"))




@app.route("/home/signinvalidate" , methods=['POST','GET'])
def signValidate():

    if request.method == "POST" :
        fname = request.form['fname']
        lname = request.form['lname']
        name = fname+" "+lname
        uname = request.form['uname']
        dept = request.form['dept']
        password = request.form['up']
        mail = request.form['mail']

        datasource.addPost(name,uname,dept,password,mail)

        return render_template("profile_camera.html" , user = uname)



@app.route("/home/<user>")
def openWelcome(user):
    return render_template("welcome.html",user=user )


@app.route("/home/<user>/gallery")
def openGallery(user):
    return render_template('gallery.html' , user = user)


@app.route("/home/staff/<user>")
def staffWelcome(user):
    return render_template("staff_welcome.html", user=user)


@app.route("/home/staff/<user>/login")
def staffLogin(user):
    return redirect(url_for('login'))

@app.route("/home/staff/<user>/create")
def createSession(user):
    return render_template('session_create.html' , user = user)


@app.route("/home/staff/<user>/action", methods=['POST','GET'])
def addSession(user):
    if request.method == "POST":
        uname = request.form["uname"]
        dept = request.form["Department"]
        sub = request.form["subject"]
        st = request.form["st"]
        et = request.form["et"]

        datasource.addSchedule(uname,dept,sub,st,et)
        return redirect(url_for("staffWelcome", user = uname))

@app.route("/home/staff/<user>/logout")
def logoutStaff(user):
    # user_list.pop(user)
    session.pop('uname')
    return redirect(url_for('message'))



@app.route("/home/loginValidate", methods=['POST','GET'])
def loginValidate():

    if request.method == "POST" :
        uname = request.form['uname']
        password = request.form['pass']

        res,desig = datasource.checkPost(uname,password)

        if res:

            if desig == "t" :
                session['uname'] = uname
                return redirect(url_for('staffWelcome',user = uname))

            temp = user(uname,VideoCamera(uname))
            user_list[uname] = 0
            session['uname']=uname
            global vid
            vid = VideoCamera(uname)
            return redirect(url_for('openWelcome',user=uname))


        return render_template("login.html" , wrong=1)



@app.route("/home/<user>/<id>/webcam")
def showWebcam(user,id):
    print(id)
    return render_template('webcam.html',user = user , sid = id)



@app.route("/home/<user>/logout")
def logout(user):
    # user_list.pop(user)
    session.pop('uname')
    return redirect(url_for('message'))




@app.route("/about")
@app.route("/home/about")
def about():
    return render_template('about.html')

@app.route("/home/<user>/about")
def user_about(user):
    return redirect(url_for('about'))

@app.route("/home/<user>/about")
def log_abt(user):
    return redirect(url_for('about'))


@app.route("/home/<user>/list_gallery")
def list_gallery(user):
    return render_template('list_gallery.html' , user = user)




@app.route("/home/<user>/profile")
def showProfile(user):
    res = datasource.getUserDetails(user)
    res[0]["dept"] = dept[res[0]["dept"]]
    return render_template('profile.html' , user_det = res[0])



@app.route("/home/<user>/session_over")
def endSession(user):
    return render_template("session_over.html",user = user)


@socket_.on('check' , namespace='/test')
def check(message) :
    print('checking')
    us = message['user']
    try:
        if session['uname'] != None and  us == session['uname'] :

            emit('validity' , {'status' : "ok"})

        else:

            emit('validity' , {'status' : "notok"})

    except KeyError as e :
        emit('validity', {'status': "notok"})



@socket_.on('profile_pic' , namespace='/test1')
def uploadProfile(message):
    print('uploading profile to db')
    image = message['data']

    us = message['user']

    datasource.uploadProfile(us , image)



@socket_.on('send_gallery_image' , namespace='/trial')
def uploadToDb(message):
    print('sending')
    image = message['data']

    us = message['user']

    datasource.addImage(us, image)




@socket_.on('gallery_send' , namespace = '/receive')
def sendToClient(message):
    print('sending to client')

    us = message['user']

    images = datasource.receiveImage(us)

    if len(images) == 0 :
        emit('vechiko_image', {'data': "0"})
        return


    for image in images :
        # b_64 = base64.b64encode(image)
        # b_64 = str(b_64)
        # b_64 = b_64[2:]
        # b_64 = prefix+b_64
        # b_64 = b_64[0 : -1]

        emit('vechiko_image' , {'data' : image})


@socket_.on('get_staff_schedules' , namespace='/test')
def getStaffSession(message):
    print('get staff schedules')
    us = message['user']
    schedules = datasource.getStaffSchedules(us)

    emit('no_of_staff_schedules', {'num': len(schedules)})

    print(len(schedules))
    for schedule in schedules:
        schedule['dept'] = dept[schedule['dept']]

        emit('staff_session', {'user': us, 'dept': schedule['dept'], 'sub': schedule['sub'], 'start': schedule['start'],
                               'end': schedule['end'], 'id': schedule['id']})


@socket_.on('get_schedules',namespace='/test')
def getSessions(message):
    print('get schedules')
    us = message['user']
    deptt = datasource.getDept(us)
    schedules = datasource.getSchedules(deptt)

    emit('no_of_schedules',{'num' : len(schedules)})

    print(len(schedules))
    for schedule in schedules:

        schedule['dept'] = dept[schedule['dept']]

        emit('session' , {'user' : us,'dept':schedule['dept'] ,'sub' : schedule['sub'] , 'start' : schedule['start'] , 'end' : schedule['end'],'id' : schedule['id']})



def sendMail(sub,att,to):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login('cipproject21@gmail.com', 'tothemoon_2021')
        msg = '{} attendance percentage\n\nYour attendance percentage : {} '.format(sub, att)
        server.sendmail('cipproject21@gmail.com',to, msg)
        server.quit()
        print('Successful!!!')
    except Exception as e:
        print(e)
        print('Failed')


def find_diff(start, end):
    x = start.split(":")
    y = end.split(":")

    hr = (int(y[0]) - int(x[0])) * 60 * 60

    mins = (int(y[1]) - int(x[1])) * 60
    if mins < 0:
        mins = mins * -1

    sec = (int(y[2]) - int(x[2]))
    if sec < 0:
        sec = (sec * -1)


    return hr + mins + sec



@socket_.on('send_image',namespace='/test')
def getImage(message):
    print('success')
    image=message['data']

    img=image.split(",")[1]

    img=base64.b64decode(img)

    us=message['user']
    id = message['sid']

    sch = datasource.getScheduleById(id)

    now = datetime.now()

    cur = now.strftime("%H:%M:%S")
    try :
        if sch['end'] < cur:

            dept = sch["dept"]

            list = datasource.getMail(dept)

            for l in list:
                to = l['mail']
                df = pd.read_csv("./attend.csv")
                loc = df.loc[df['REGNO'] == int(l['uname'])]
                tot = df.loc[loc.index[0], 'TOTAL']
                start = sch['start']
                end = sch['end']

                diff = find_diff(start , end)

                percentage = (tot / diff) * 100

                df.loc[loc.index[0], 'TOTAL']=0

                th = threading.Thread(target=sendMail, args=(sch['sub'], str(percentage) + '%', to))
                th.start()


            emit("session_over" , {'user' : us})

    except Exception as e:
        print("Key error")

    global vid

    if vid == None :
        vid = VideoCamera(us)

    filename="./temp/"+us+".png"

    with open(filename, 'wb') as f:
        f.write(img)

    #datasource.addImage(us,image)

    thread_lock.acquire()

    vid.get_frame()

    thread_lock.release()




if __name__ == "__main__":
    socket_.run(app,debug=True)


