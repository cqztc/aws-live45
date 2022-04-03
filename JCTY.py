from flask import Flask, render_template, request, url_for
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__,template_folder='templates')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
#table = 'employee'                                                          #NO IMPORTANT?


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route("/empDatabase", methods=['GET', 'POST'])
def employeeDatabase():
    return render_template('EmployeeSystem.html')

@app.route("/empDatabase1", methods=['GET', 'POST'])
def employeeDatabase1():
    return render_template('AddEmp.html')



@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    employee_name = request.form['employee_name']
    job_role = request.form['job_role']
    salary = request.form['salary']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s)"             #CHANGE TABLE NAME?
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, employee_name, job_role, salary))
        db_conn.commit()
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')
        number_of_rows = cursor.execute("SELECT * FROM employee")

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('OutputEmployeeSystem.html', employee_id = emp_id, name=employee_name, jobrole=job_role,month_salary=salary, number_of_rows=number_of_rows)




@app.route("/addemp1", methods=['POST'])
def AddEmp1():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    date = request.form['currentDate1']
    time = request.form['currentTime1']
 

    insert_sql = "INSERT INTO employee_at VALUES (%s, %s, %s, %s)"             #CHANGE TABLE NAME?
    cursor = db_conn.cursor()

    cursor.execute(insert_sql, (emp_id, first_name, date, time))
    db_conn.commit()
    emp_num = emp_id
    emp_name = first_name
    date_now = date
    timenow = time

    cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name, id = emp_num, date_1 = date_now, time_1 =timenow )



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
