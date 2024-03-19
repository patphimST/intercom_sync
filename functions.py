import requests
import config
import pandas as pd
import re
from pymongo import MongoClient
from bson.objectid import ObjectId

import dns.resolver
dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers=['8.8.8.8']

client = MongoClient(f'mongodb+srv://{config.mongo_pat}')
db = client['legacy-api-management']
col_soc = db["societies"]
col_it = db["items"]
col_users = db["users"]

def get_user(df):
    l_intercomId = []
    for i in range(len(df)):
        user_email = df['user_email'][i]

        url = f"https://api.intercom.io/contacts/search"
        payload = {
            "query": {
                "operator": "AND",
                "value": [
                    {
                        "field": "email",
                        "operator": "~",
                        "value": f"{user_email}"
                    }
                ]
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Intercom-Version": "2.10",
            'Authorization': f'Bearer {config.api_intercom}'}

        response = requests.post(url, json=payload, headers=headers)
        response = response.json()
        print(user_email,response)
    #     # intercomId = response["data"][0]["id"]
    #
    # df['intercomId'] = l_intercomId
    # df.to_csv('csv/delete_ok.csv')

def get_id_company(ent):
    url = "https://api.intercom.io/companies"

    query = {
        "name": f"{ent}",
    }

    headers = {
        "Intercom-Version": "2.10",
        "Authorization": f"Bearer {config.api_intercom}"
    }

    response = requests.get(url, headers=headers, params=query)

    data = response.json()['id']
    print(data)
    return data

def get_user_bdd(ent):
    l_id, l_member, l_name = [], [], []
    search = ent
    search_expr = re.compile(f".*{search}.*", re.I)
    cursor = col_soc.find({'name': {'$regex': search_expr}})
    for rep in cursor:
        l_member.append(len(rep["members"]))
        l_id.append(rep["_id"])
        l_name.append(rep["name"])

    df = pd.DataFrame(list(zip(l_id, l_member, l_name)), columns=['id', 'members', 'name'])
    df = (df[df.members == df.members.max()])
    my_id = (df['id'].values[0])
    cursor_soc = col_soc.find({'_id': my_id})

    l_user_firstname,l_user_lastname = [],[]
    l_access = []
    l_user_email = []
    l_iduser = []
    l_intercom = []
    l_full = []
    l_phone = []
    for c in cursor_soc:
        len_members = (len(c["members"]))
        l_members = [c['members'][x]['user'] for x in range(len_members)]
        for i in l_members:
            cursor_user = col_users.find({'_id': i})
            for d in cursor_user:
                first = d['firstname'].capitalize()
                last = d['lastname'].upper()
                l_iduser.append(d['_id'])
                l_access.append(d['unaccessible'])
                l_user_firstname.append(d['firstname'])
                l_user_lastname.append(d['lastname'])
                l_user_email.append(d['email'])
                l_full.append(f"{first} {last}")
                try:
                    l_intercom.append(d['intercomId'])
                except:
                    l_intercom.append("")
                print(d['email'],d['unaccessible'])
                try:
                    l_phone.append(d['phone'])
                except:
                    l_phone.append("")
                print(d['email'],d['unaccessible'])
    org_df = pd.DataFrame(list(zip(l_iduser,l_user_email,l_phone,l_user_lastname,l_user_firstname,l_full,l_access,l_intercom)), columns=['id_user','user_email','phone',"user_first","user_last","full_name",'unaccessible','intercom'])
    org_df['unaccessible'] = org_df['unaccessible'].replace(False,'Ouvert')
    org_df['unaccessible'] = org_df['unaccessible'].replace(True,'Sans accès')
    org_df.to_csv(f"csv/{ent}_user_access.csv",index=False)
    
def list_tagid():
    import requests

    url = "https://api.intercom.io/tags"

    payload = {}
    headers = {
        'Authorization': f'Bearer {config.api_intercom}'}
    

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

def get_user_with_email(email):
    url = "https://api.intercom.io/contacts/search"

    payload = {
        "query": {
            "operator": "AND",
            "value": [
                {
                    "field": "email",
                    "operator": "=",
                    "value": email
                }
            ]
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Intercom-Version": "2.10",
        'Authorization': f'Bearer {config.api_intercom}'
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()['data']

    l_email,l_intercomId=[],[]
    for i in range (len(data)):
        intercomId = (data[i]['id'])
        user_email = data[i]["email"]
        print(intercomId,user_email)

        l_email.append(user_email)
        l_intercomId.append(intercomId)
    df = pd.DataFrame({'intercomId': l_intercomId, 'email': l_email})
    df.to_csv("csv/extract_from_email.csv")

def attach_user_to_company(intercomId_user,intercomId_company):

    url = f"https://api.intercom.io/contacts/{intercomId_user}/companies"

    payload = {
        "id": f"{intercomId_company}"
    }

    headers = {
        "Content-Type": "application/json",
        "Intercom-Version": "2.10",
        'Authorization': f'Bearer {config.api_intercom}'
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    print(data)
    return (data)

def simple_update_user(intercomId):
    import requests

    url = f"https://api.intercom.io/contacts/{intercomId}"

    payload = {
        "custom_attributes": {
            "Workplace": "OK" }
        }


    headers = {
        "Content-Type": "application/json",
        "Intercom-Version": "2.10",
        'Authorization': f'Bearer {config.api_intercom}'
    }

    response = requests.put(url, json=payload, headers=headers)

    data = response.json()
    print(data)

def update_user(intercomId, user_id,fullname,phone,unaccessible, roles):
    import requests

    url = f"https://api.intercom.io/contacts/{intercomId}"

    payload = {
        "name": fullname,
        "phone": phone,
        "external_id": user_id,
        "custom_attributes": {
            "role_in_company":roles,
            "unaccessible": unaccessible}
        }



    headers = {
        "Content-Type": "application/json",
        "Intercom-Version": "2.10",
        'Authorization': f'Bearer {config.api_intercom}'
    }

    response = requests.put(url, json=payload, headers=headers)

    data = response.json()
    print(data)

def delete_contact(user_id):
    url = f"https://api.intercom.io/contacts/{user_id}]"

    headers = {
        "Intercom-Version": "2.10",
        'Authorization': f'Bearer {config.api_intercom}'
    }

    response = requests.delete(url, headers=headers)

    data = response.json()
    print(data)

def unarchive(intercomId):
    import requests

    url = "https://api.intercom.io/contacts/" + intercomId+ "/unarchive"

    headers = {
        "Intercom-Version": "2.10",
        "Authorization": f"Bearer {config.api_intercom}"
    }

    response = requests.post(url, headers=headers)

    data = response.json()
    print(data)