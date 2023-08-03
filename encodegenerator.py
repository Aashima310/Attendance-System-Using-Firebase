import cv2
import os
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-c6cf6-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-c6cf6.appspot.com"
})


#lets import faces
folderpath= 'images'
pathimg= os.listdir(folderpath)
#print(pathimg)
imglists= []
stdid=[] #import ids
for path in pathimg:
    imglists.append(cv2.imread(os.path.join(folderpath,path)))
    #print(os.path.splitext(path)[0]) #to get ids ie image name
    stdid.append(os.path.splitext(path)[0])

    #little bit storage bucket vala kaam DB
    filename=f'{folderpath}/{path}'
    bucket= storage.bucket()
    blob= bucket.blob(filename)
    blob.upload_from_filename(filename)
    #storage bucket vala kaam end


#print(len(imglists))
#print(stdid)


#to run encodings
#loop thro' all images and encode all imgs
def findencodes(imglists):
    encodelist=[]
    for img in imglists:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) #bcz face recgnition used rgb whereas cv2 was using bgr
        encode= face_recognition.face_encodings(img)[0]  #find encodings of that image [0] means we provided ist element of that image
        encodelist.append(encode)
    return encodelist

print("encoding started.....")
encodelistknown = findencodes(imglists)
#print(encodelistknown)
encodelistknownwithid = [encodelistknown, stdid]
print("encoding complete")

#now we have to save it in pickle file so that we can
#import it while using webcam
file=open("encodefile.p", 'wb')
pickle.dump(encodelistknownwithid, file)
file.close()
print("file saved")

