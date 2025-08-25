# import ee
# ee.Initialize(project='gee-assignment-469904')
# info  = ee.AccountInfo()
# print(info.getInfo())


import ee

credentials = ee.Credentials()
print(credentials.get("client_email"))  # This will show the email of the service account or user account
