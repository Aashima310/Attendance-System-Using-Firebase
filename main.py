import cv2
import os
import pickle
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-c6cf6-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-c6cf6.appspot.com"
})
bucket=storage.bucket()

img2 = cv2.VideoCapture(1)
img2.set(3,640)
img2.set(4,480)
img2.set(10,1000)


imgbackgrnd=cv2.imread('resources/background.png')

#importing modes from resources
foldermode= 'resources/Modes'
pathmode= os.listdir(foldermode)
modelist= []
for path in pathmode:
    modelist.append(cv2.imread(os.path.join(foldermode,path)))


#import/load the encoding file
print("loading Encode file started...")
file=open('encodefile.p','rb')
encodelistknownwithid = pickle.load(file) #now it contains faceencodings and std id
file.close()
#so we need to seprate them now
encodelistknown, stdid= encodelistknownwithid
print("Encode file loaded!!")
#print(stdid)


modetype=0
counter=0
idtobedownloaded=-1
imagestd=[]

while True:
    success, imgg = img2.read()

    imgs=cv2.resize(imgg, (0, 0) , None, 0.25, 0.25)
    imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)

    #feed values to face rec system - faces in current frame , encodings in the current frame
    facecurrentframe= face_recognition.face_locations(imgs)
    encodingsofcurrframe= face_recognition.face_encodings(imgs,facecurrentframe)


    imgbackgrnd[162:162+480, 55:55+640]= imgg
    imgbackgrnd[44:44+633, 808:808+414] = modelist[modetype] #mode number 0,1,2,3 in imglist[]


    if facecurrentframe:
        # loop through all the known encodings and check if the currentframe encodings match
        # with any of the photo
        for encodeface, faceloc in zip(encodingsofcurrframe, facecurrentframe):
            matches = face_recognition.compare_faces(encodelistknown, encodeface)
            distance = face_recognition.face_distance(encodelistknown, encodeface)
            # kitna match , lower the dist value better the match
            # print("matches",matches)
            # print("distance",distance)

            # istly get index of least distance
            matchindex = np.argmin(distance)
            # print("match index" , matchindex)

            if matches[matchindex]:
                # print("known face detected")
                # print(stdid[matchindex])
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # bcz we have reduced imagesize earlier (imgs)
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgbackgrnd = cvzone.cornerRect(imgbackgrnd, bbox, rt=0)  # rect thickness
                idtobedownloaded = stdid[matchindex]
                if counter == 0:
                    #these 3 lines are bcz screen lags after we cover our face
                    #to collect data
                    #as we are not using asynchronous functions here
                    #so we adding LOADING to make it look less bad
                    cvzone.putTextRect(imgbackgrnd,"loading",(275,400))
                    cv2.imshow("facerecognition", imgbackgrnd)
                    cv2.waitKey(1)

                    counter = 1
                    modetype = 1
        if counter != 0:
            if counter == 1:
                # download student info
                stdinfo = db.reference(f'students/{idtobedownloaded}').get()
                print(stdinfo)
                # getimagefrom storage
                blob = bucket.get_blob(f'images/{idtobedownloaded}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imagestd = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # update data of number of attendance
                datetimeobj = datetime.strptime(stdinfo['last_attendance_time'],
                                                "%Y-%m-%d %H:%M:%S")
                secondselapse = (datetime.now() - datetimeobj).total_seconds()
                if secondselapse > 30:
                    ref = db.reference(f'students/{idtobedownloaded}')
                    stdinfo['total_attendance'] += 1
                    ref.child('total_attendance').set(stdinfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modetype = 3
                    counter = 0
                    imgbackgrnd[44:44 + 633, 808:808 + 414] = modelist[modetype]

            if modetype != 3:
                if 10 < counter < 20:
                    modetype = 2
                imgbackgrnd[44:44 + 633, 808:808 + 414] = modelist[modetype]

                if counter <= 10:
                    cv2.putText(imgbackgrnd, str(stdinfo['total_attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (255, 255, 255), 1)
                    cv2.putText(imgbackgrnd, str(stdinfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(imgbackgrnd, str(idtobedownloaded), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(imgbackgrnd, str(stdinfo['standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    cv2.putText(imgbackgrnd, str(stdinfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    cv2.putText(imgbackgrnd, str(stdinfo['starting_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)

                    (width, height), _ = cv2.getTextSize(stdinfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - width) // 2  # 414 is width of total place to write the name
                    cv2.putText(imgbackgrnd, str(stdinfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (50, 50, 50), 1)
                    imgbackgrnd[175:175 + 216, 909:909 + 216] = imagestd

                counter += 1

                if counter >= 20:
                    counter = 0
                    modtype = 0
                    stdinfo = []
                    imagestd = []
                    imgbackgrnd[44:44 + 633, 808:808 + 414] = modelist[modetype]
    else:
        modetype=0
        counter=0


    cv2.imshow("facerecognition",imgbackgrnd)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break