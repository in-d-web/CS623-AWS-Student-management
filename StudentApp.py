import io

from flask import Flask, render_template, request
from pymysql import connections
import sys
import boto3
import os
from config import *
from PIL import Image
import json

app = Flask(__name__)

bucket = awsbucket
region = awsregion

db_conn = connections.Connection(
    host=apphost,
    port=3306,
    user=appuser,
    password=apppass,
    db=appdb
)


output = {}
table = 'student'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('admin.html')


@app.route("/gotoadd", methods=['GET', 'POST'])
def gotoadd():
    return render_template('addstudent.html')


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route("/addstudent", methods=['POST'])
def AddStudent():
    net_id = request.form['net_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    major = request.form['major']
    location = request.form['location']
    student_image_file = request.files['student_image_file']

    insert_sql = "INSERT INTO student VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:

        cursor.execute(insert_sql, (net_id, first_name,
                       last_name, major, location))
        db_conn.commit()
        student_name = "" + first_name + " " + last_name
        # Upload image file to S3 bucket #
        student_image_file_name_in_s3 = "net-id-" + str(net_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(awsbucket).put_object(
                Key=student_image_file_name_in_s3, Body=student_image_file)
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=awsbucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                awsbucket,
                student_image_file_name_in_s3)

        except Exception as e:
            print(e)
            return render_template('Error1.html')

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('StudentAdd_Success.html', name=student_name)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    return render_template("admin.html")


@app.route("/getstudent", methods=['GET', 'POST'])
def GetStudent():
    return render_template("GetStudentInfo.html")


@app.route("/fetchdata", methods=['POST'])
def FetchStudent():
    net_id = request.form['net_id']

    output = {}
    select_sql = "SELECT netid, fname, lname, major, location from student where netid=%s"
    cursor = db_conn.cursor()
    student_image_file_name_in_s3 = "net-id-" + str(net_id) + "_image_file"
    s3 = boto3.resource('s3')

    bucket_location = boto3.client(
        's3').get_bucket_location(Bucket=awsbucket)
    s3_location = (bucket_location['LocationConstraint'])

    if s3_location is None:
        s3_location = ''
    else:
        s3_location = '-' + s3_location

    image_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
        s3_location,
        awsbucket,
        student_image_file_name_in_s3)

    try:
        cursor.execute(select_sql, (net_id))
        result = cursor.fetchone()

        output["net_id"] = result[0]
        print('EVERYTHING IS FINE TILL HERE')
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["major"] = result[3]
        output["location"] = result[4]
        print(output["net_id"])

        return render_template("StudentInfo_Output.html", id=output["net_id"], fname=output["first_name"],
                               lname=output["last_name"], major=output["major"], location=output["location"], image_url=image_url)

    except Exception as e:
        print(e)
        return render_template('Error2.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
