import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-c6cf6-default-rtdb.firebaseio.com/"
})

ref= db.reference('students')   #create student directory
data= {
    "12":  #key
        { #inside it are all the values
            "name":  "Rachel green",
            "major": "Fashion",
            "starting_year": "2020",
            "total_attendance": 6,
            "standing": "G",
            "year":4,
            "last_attendance_time": "2023-07-22 00:54:34"
        },
    "34":  #key
        { #inside it are all the values
            "name":  "Joey Tribianni",
            "major": "Acting",
            "starting_year": "2020",
            "total_attendance": 12,
            "standing": "B",
            "year":4,
            "last_attendance_time": "2023-07-22 00:54:34"
        },
    "56":  #key
        { #inside it are all the values
            "name":  "Monica Geller",
            "major": "Hotel Management",
            "starting_year": "2022",
            "total_attendance": 7,
            "standing": "G",
            "year":2,
            "last_attendance_time": "2023-07-22 00:54:34"
        },
    "78":  #key
        { #inside it are all the values
            "name":  "Aashima Garg",
            "major": "B.Tech",
            "starting_year": "2020",
            "total_attendance": 6,
            "standing": "G",
            "year":4,
            "last_attendance_time": "2023-07-22 00:54:34"
        },
}
for key, value in data.items():
    ref.child(key).set(value)
#child means particular directory
