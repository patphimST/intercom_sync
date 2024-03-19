import pandas as pd
from functions import *


df = pd.read_csv('csv/eureden.csv')
df_phone_vide = df.loc[df['phone'].isnull()].reset_index()
df['phone'].fillna("-", inplace=True)


for i in range (len(df)):
    email = (df['email'][i])
    intercomId = (df['intercomId'][i])
    phone = (df['phone'][i])
    unaccessible = str(df['unaccessible'][i])
    user_id = (df['user_id'][i])
    fullname = (df['fullname'][i])
    roles = (df['roles'][i])
    # try:
    #     unarchive(intercomId)
    # except:
    #     print(email, "> failed")
    # try:
    #     update_user(intercomId, role)
    # except:
    #     print(email, "> failed")
    # try:
    #     attach_user_to_company(intercomId,"65cb2f217a3b109a08df470d")
    # except:
    #     print(email,"> company failed")
    try:
        update_user(intercomId, user_id,fullname,phone,unaccessible, roles)
    except :
        print(email, "> failed")





# get_user_with_email("jean-francois.briere@eureden.com")