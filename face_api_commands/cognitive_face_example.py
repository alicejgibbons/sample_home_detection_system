# CHANGE ME
name = '' 

import cognitive_face as CF
key = ''
local_image_path = './images/' + name.replace(" ", "") + '.jpg'
CF.Key.set(key)
BASE_URL = ''  # Replace with your regional Base URL
CF.BaseUrl.set(BASE_URL)

groupID = ''
#Already created group
#CF.person_group.create(groupID)

######################################
# ### Create person or face in list
# 
# - Create Group
# - Create Person to Group
# - Add image to Person
# - Train

#if you need to delete a person
#deleted_person =  CF.person.delete(groupID, '')


#FIRST check if peson is in the group already
person_list = CF.person.lists(groupID)
person_list


# IF they don't exist:
# Create New person in list
result_create_person = CF.person.create(groupID,name)
result_create_person

CF.person.add_face(local_image_path, groupID, result_create_person['personId']) # returns a persisted face id that gets added to list

# ELSE
# Add their face to a list 

CF.person.add_face(local_image_path, groupID, 'PERSON ID') # returns a persisted face id that gets added to list


# Check new person list
person_list = CF.person.lists(groupID) 
person_list


# train model on new face/ person
CF.person_group.train(groupID)


################################################
# ### Identify people in Photos

result = CF.face.detect(local_image_path)
result


face_ids = [each['faceId'] for each in result]


results_identify = CF.face.identify(face_ids,groupID)
results_identify


person_ids = [each['candidates'][0]['personId'] for each in results_identify if len(each['candidates']) > 0]
person_ids


CF.person.get(groupID,person_ids[0])['name']

