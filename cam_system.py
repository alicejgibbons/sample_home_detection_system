import json
import time
import requests
import pyodbc
import db_access
import os
import io
#from picamera import PiCamera
from azure.storage.blob import BlockBlobService

#PI ID
floorplanid = 2

with open('settings.json') as f:
    settings = json.load(f)

# Face API request info
face_url = 'https://westus2.api.cognitive.microsoft.com/face/v1.0/'
params_detect = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender'
}
header_detect = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': settings['cog_face_key']
}
header_identify = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': settings['cog_face_key']
}

# how long this runs for = approx. how many iterations * 3 seconds
how_many_iterations = 1

if __name__ == "__main__":
    #camera = PiCamera()
    #camera.rotation = 180
    #camera.brightness =  55

    #initial sleep for camera to warm up
    #time.sleep(2)
    print("\nHERE-4")
    #Takes some time
    db = db_access.Db()
    
    for i in range(how_many_iterations):
        local_path = os.path.expanduser("./images/")
        local_file_name = "AliceGibbons.jpg"
        #local_file_name = "capture{}.jpg".format(i)
        full_path_to_file = os.path.join(local_path, local_file_name)

        print("\nHERE-3")

        #camera.capture(full_path_to_file)
        #img = open(os.path.expanduser(full_path_to_file,'rb')
        img = open(os.path.expanduser(full_path_to_file),'rb')

        # Establish blob service connection
        print("\nHERE-2")
        block_blob_service = BlockBlobService(settings['account_name'], settings['account_key'])
        print("\nHERE-1")


        print("HERE")

        if os.path.isfile(full_path_to_file):
            #file exists
            print("File exists at: " + full_path_to_file)
        else:
            #file dne
            print("File does not exist: " + full_path_to_file + ". Exiting...")
            exit(1)

        print("HERE1")

        print("\nUploading to Blob storage as: " + local_file_name)

        # Upload the created file, use local_file_name for the blob name
        block_blob_service.create_blob_from_path(settings['container_name'], local_file_name, full_path_to_file)

        # Get the blob url 
        blob_url = block_blob_service.make_blob_url(settings['container_name'], local_file_name)
        print("Blob url is: " + blob_url)

        # Refreshes the 'new URL' corresponding to the floor plan location in SQL DB
        db.update_lounge_image(floorplanid,blob_url)

        #refresh lounge person database
        db.refresh_lounge_person(floorplanid)
        
        #face detection
        response = requests.post(
            face_url + 'detect',
            data = img,
            headers = header_detect,
            params = params_detect
        )

        if response.text:
            result = response.json()
            print("Result is" + str(result))
        else:
            result = {}
            print("No response, exiting.. " + str(response))
            exit(1)
        
        face_ids = [each['faceId'] for each in result]

        # if there are faces detected
        if len(face_ids) > 0:

            print("Face(s) detected in photo")
            
            #run faces against person group for person identification
            json = {
                'personGroupId': settings['person_group_id'],
                'largePersonGroupId': None,
                'faceIds': face_ids,
                'maxNumofCandidateReturned':1,
                'confidenceThreshold': None
            }
            
            response = requests.post(
                face_url + 'identify',
                json = json,
                headers = header_identify
            )

            if response.text:
                result = response.json()
            else:
                result = {}

            person_ids = [each['candidates'][0]['personId'] for each in result if len(each['candidates']) > 0]
            print("Person IDs identified: " + str(person_ids))

            #if there are people identified, edit names in database
            if len(person_ids) > 0:
                for id in person_ids:
                    response = requests.get(
                        face_url + 'persongroups/{}/persons/{}'.format(settings['person_group_id'],id),
                        headers = header_identify
                    )
                    if response.text:
                        result = response.json()
                    else:
                        result = {}

                    db.insert_lounge_person(floorplanid,result['name'])
                    print('Found ' + result['name'])

    db.cnn.close()
                    
