import os

apphost = "student.cmojbf7a9vmd.us-west-2.rds.amazonaws.com"
appuser = "admin"
apppass = "qazqazqaz"
appdb = "student"
awsbucket = "addstudent01"
awsregion ="us-west-2c"
adminusername= os.environ.get('adminpassword') or "admin"
adminpassword= os.environ.get('adminpassword') 
