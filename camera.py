
import pandas as pd
import csv
import cv2

from datetime import datetime
import face_recognition
import pickle
import os
# from model import svc



class VideoCamera(object):

    def __init__(self,user):
        print('VideoCam initialized')
        filename = 'face_recognition_model.sav'
        self.svc = pickle.load(open(filename, 'rb'))
        self.unamee = user


    def __del__(self):
        print('videocam is off' , self.unamee)
        self.add_csv('0')


    # def predict_Out(imgg):

    def add_csv(self,res):
        df = pd.read_csv("./attend.csv")

        print(self.unamee,res)

        if res == '':
            res = '0'

        if res == self.unamee:
            f = 0
            print('eq')
            loc = df.loc[df['REGNO'] == int(res)]

            try:
                loc.index[0]
            except IndexError as e:
                s = df.shape[0]
                df.loc[s, 'REGNO'] = int(self.unamee)
                df.loc[s, 'TOTAL'] = 0

            loc = df.loc[df['REGNO'] == int(res)]
            ot = df.loc[loc.index[0], 'TOTAL']
            df.loc[loc.index[0], 'TOTAL'] = ot +1

        else :
            print('neq')


            #     df.loc[s, 'IN'] = datetime.now().strftime('%H:%M:%S')
            #     df.loc[s, 'OUT'] = 0
            #     df.loc[s, 'TOTAL'] = 0
            #     f = 1
            #
            # if f == 0:
            #     t = df.loc[loc.index[0], 'IN']
            #     if t == 0:
            #         print('in ' + reg_no)
            #         df.loc[loc.index[0], 'IN'] = datetime.now().strftime('%H:%M:%S')



        # else:
        #     ff = 0
        #     loc = df.loc[df['REGNO'] == int(self.unamee)]
        #     t=0
        #     try:
        #         t = df.loc[loc.index[0], 'IN']
        #     except IndexError as e:
        #         ff = 1
        #     if t != 0 and ff == 0:
        #         df = pd.read_csv("./attend.csv")
        #         loc = df.loc[df["REGNO"] == int(self.unamee)]
        #         df.loc[loc.index[0], 'OUT'] = datetime.now().strftime('%H:%M:%S')
        #         diff = self.find_diff(df['IN'][loc.index[0]], df['OUT'][loc.index[0]])
        #         old = df.loc[loc.index[0], 'TOTAL']
        #         df.loc[loc.index[0], 'TOTAL'] = old + diff
        #         df.loc[loc.index[0], 'IN'] = 0
        #         df.loc[loc.index[0], 'OUT'] = 0

        df.to_csv("./attend.csv", index=False)



    def get_frame(self):
        print('inside getframe')
        self.unamee

        image = cv2.imread("./temp/"+self.unamee+".png")

        imgg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        face_loc = face_recognition.face_locations(imgg)

        if len(face_loc) == 0:
            self.add_csv('0')


        else:
            face_enc = face_recognition.face_encodings(imgg, face_loc)
            for a, b in zip(face_enc, face_loc):
                res = self.svc.predict([a])
                res=res[0]
                self.add_csv(res)


