import json
import os
# Consumer Key: ******
# Consumer Secret: **********
consumer_key = u"your_consumer_key"
consumer_secret = u"your-consumer-secret"
notebook_name = u"your-notebook-name"

app_data = {
    "dev_token": "", 
    "sandbox": False, 
    "consumer_secret": consumer_secret, 
    "token": "", 
    "china": False, 
    "HOST_URL": "http://localhost:8080", 
    "consumer_key": consumer_key
}

note_data = {
    "notebooks": [
        {
            "guid": "",
            "name": notebook_name
        }
    ],
    "notes": [],
    "updateCount": 0,
    "tags": [
        {
            "guid": "",
            "name": "MakeContents"
        }
    ]
}


here = os.path.dirname(__file__)

with open(here + '/app_data.json', 'wb') as f:
            json.dump(app_data, f)

with open(here + '/note_data.json', 'wb') as f:
            json.dump(note_data, f)