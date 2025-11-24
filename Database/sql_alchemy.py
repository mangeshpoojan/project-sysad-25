#imports
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import render_template
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess

# database creation
BASE_DIR = os.getcwd()
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_FOLDER, exist_ok=True)
DATABASE_PATH = os.path.join(DATA_FOLDER, 'Submission.db')

app = Flask('SubmissionBackend')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ===== INITIALIZE DB & MARSHMALLOW =====
db = SQLAlchemy(app)
ma = Marshmallow(app)

class submission(db.Model):
    auto_increment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Subject = db.Column(db.String(100))
    CourseCode = db.Column(db.String(20))
    TestNo = db.Column(db.Integer)
    StudentID = db.Column(db.String(20))
    SeatNo = db.Column(db.String(20),default='N/A')
    Lab = db.Column(db.String(20),default='N/A')
    Submitted = db.Column(db.Boolean, default=False)
    TimeStamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo('Asia/Kolkata')))
 
# ===== CREATE Table in DB =====
with app.app_context():
    db.create_all()


# ===== SCHEMA FOR SERIALIZATION =====
class SubmissionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = submission
        load_instance = True 
        fields = ('Subject', 'CourseCode', 'TestNo', 'StudentID', 'SeatNo', 'Lab' , 'Submitted', 'TimeStamp')  
 

# Adding Sample Data
with app.app_context():
    if submission.query.count() == 0:
        submission_Sl_lab_1 = [
            submission(Subject='software_lab', CourseCode='cs699', TestNo=1, StudentID='25m0828', SeatNo='1', Lab='sl1' ,Submitted=True),
            submission(Subject='software_lab', CourseCode='cs699', TestNo=1, StudentID='25m0829', SeatNo='2', Lab='sl1' ,Submitted=True),
            submission(Subject='software_lab', CourseCode='cs699', TestNo=1, StudentID='25m0830', SeatNo='3', Lab='sl1' ,Submitted=False),
        ]
        db.session.add_all(submission_Sl_lab_1)
        db.session.commit()
        print("Sample data added to the database.")

# ===== INITIALIZE SCHEMA INSTANCE =====
single_submission_schema = SubmissionSchema()
multi_submission_schema = SubmissionSchema(many=True)

# ===== TEST: QUERY AND SERIALIZE =====
with app.app_context():
    all_submissions = submission.query.all()

    result = multi_submission_schema.dump(all_submissions)
    print("All Submissions in Database:")
    print(result)

    single_result = submission.query.first()
    single_result_serialized = single_submission_schema.dump(single_result)
    print("Single Submission:")
    print(single_result_serialized)

# ===== Serving webpage =====
@app.route('/submissions', methods=['GET'])
def webpage_submissions():
    return render_template('home.html')

@app.route('/submissions/submit' , methods=['POST'])
def submissions_for_lab():
    data = request.form
    app.logger.debug(f"Received form data: {data}")
    app.logger.debug(f"TestNo: {data.get('TestNo')}, CourseCode: {data.get('CourseCode')}")

    submitted_data = submission.query.filter_by(TestNo=data.get('TestNo'), CourseCode=data.get('CourseCode')).all()
    app.logger.debug(f"Query result: {submitted_data}")
    result = multi_submission_schema.dump(submitted_data)
    app.logger.debug(f"Serialized result: {result}")

    not_submitted_data = [student for student in submitted_data if not student.Submitted]
    result = [student for student in result if student['Submitted']]
    return render_template('submissions.html', submitted_data=result , not_submitted_data=not_submitted_data)


@app.route('/student/submit',methods=['POST'])
def submission_student():
    data = request.form
    app.logger.debug(f"Received form data: {data}")

    if 'StudentID' not in data or 'CourseCode' not in data or 'Lab' not in data or 'Subject' not in data or 'TestNo' not in data or 'SeatNo' not in data:
        return "Missing StudentID or CourseCode or Lab or Subject or TestNo or SeatNo", 400

    if submission.query.filter_by(StudentID=data['StudentID'], CourseCode=data['CourseCode'] , Subject=data['Subject'], TestNo=data['TestNo']).count()==0:
        new_submission = submission(
            Subject=data['Subject'],
            CourseCode=data['CourseCode'],
            TestNo=data['TestNo'],
            StudentID=data['StudentID'],
            SeatNo=data['SeatNo'],
            Lab=data['Lab'],
            Submitted=True if data['Submitted'] == 'True' else False
        )
        submitted_data = db.session.add(new_submission)
        submitted_data = single_submission_schema.dump(new_submission)
        app.logger.debug(f"New submission added: {submitted_data}")
        db.session.commit()
        return f"Submission successful {submitted_data}", 201

    # update existing submission
    existing_data = submission.query.filter_by(StudentID=data['StudentID'], CourseCode=data['CourseCode'], TestNo=data['TestNo']).first()
    if existing_data:
        existing_data.SeatNo = data['SeatNo']
        existing_data.Submitted = True if data['Submitted'] == 'True' else False
        existing_data.TimeStamp = datetime.now(ZoneInfo('Asia/Kolkata'))
        existing_data.Lab = data['Lab']
        db.session.commit()
        existing_data = single_submission_schema.dump(existing_data)
        app.logger.debug(f"Existing submission updated: {existing_data}")
        return f"Submission updated {existing_data}", 200

    existing_data = single_submission_schema.dump(existing_data)
    app.logger.debug(f"Existing submission found: {existing_data}")

    if existing_data:
        return f"Submission already exists: {existing_data}", 400
    
    return "Error in submission", 500

@app.route('/add_student/submit',methods=['POST'])
def add_student_submission():
    data = request.form
    app.logger.debug(f"Received form data: {data}")

    students = data['StudentID'].split(',')

    app.logger.debug(f"Students to be added: {students}")

    if 'StudentID' not in data or 'CourseCode' not in data or 'Subject' not in data or 'TestNo' not in data:
        return "Missing StudentID or CourseCode or Subject or TestNo", 400
    
    submitted_students = []
    for student in students:
        if submission.query.filter_by(StudentID=student, CourseCode=data['CourseCode'] , Subject=data['Subject'], TestNo=data['TestNo']).count()==0:
            new_submission = submission(
                Subject=data['Subject'],
                CourseCode=data['CourseCode'],
                TestNo=data['TestNo'],
                StudentID=student,
                SeatNo=data['SeatNo'],
                Lab=data['Lab'],
                Submitted=False
            )
            db.session.add(new_submission)
            db.session.commit() 
            new_submission_serialized = single_submission_schema.dump(new_submission)
            app.logger.debug(f"New student added: {new_submission_serialized}")
            submitted_students.append(new_submission_serialized)

    if submitted_students:
        return f"Students added successfully: {submitted_students}", 201

    return "Student already exists", 400

@app.route('/add_student')
def add_student_page():
    return render_template('add_student.html')

@app.route('/ta_direct_submit_page')
def ta_direct_submit_page():
    return render_template('ta_direct_submit.html')

@app.route('/ta_direct_submit_page/submit',methods=['POST'])
def ta_direct_submit():
    data = request.form
    app.logger.debug(f"Received form data: {data}")

    submissions_list = submission.query.filter_by(TestNo=data.get('TestNo'), CourseCode=data.get('CourseCode')).all()
    submissions_list = multi_submission_schema.dump(submissions_list)
    app.logger.debug(f"Query result: {submissions_list}")

    results = []

    for student in submissions_list:
        app.logger.debug(f"echo 'Submitting for StudentID: {student}'\n")

        with open("bash_scripts/better_submit.sh", "r") as file:
            lines = file.readlines()
        
        with open("bash_scripts/better_check.sh", "r") as file:
            check_lines = file.readlines()

        with open("bash_scripts/sending_submit.sh", "w") as file:
            file.write("#!/bin/bash\n")
            # file.write(f"check submission_{student['StudentID']}\n")
            file.write(f"DIR=\"/home/sysad/Desktop/submission_{student['StudentID']}\"\n") 
            file.write("SESSION=sysad\n")
            file.write("COURSE_CODE=" + data['CourseCode'] + "\n")
            file.write("TEST_NO=" + data['TestNo'] + "\n")
            file.write("ROLLNO=" + student['StudentID'] + "\n")
            file.write(f"FILENAME=/home/sysad/Desktop/{student['Lab']}-{student['SeatNo']}_submission_{student['StudentID']}.tar.gz\n")

            for line in check_lines:
                file.write(line)

            # file.write("SUBJECT=" + data['Subject'] + "\n") #already in db

            for line in lines:
                file.write(line)

        if student['Lab'] == "sl1":
            student_ip = "10.130.153." + student['SeatNo']
        elif student['Lab'] == "sl2":
            student_ip = "10.130.154." + student['SeatNo']
        elif student['Lab'] == "sl3":
            student_ip = "10.130.155." + student['SeatNo']
        else:
            app.logger.error(f"Invalid Lab for StudentID: {student}")
            return f"Invalid Lab for StudentID: {student['StudentID']}", 400
        

        with open("bash_scripts/file_sending_script.sh", "w") as file:
            file.write("#!/bin/bash\n")
            file.write(f"sshpass -f \"/home/umang/dank/cs699/Course_project_git/password.txt\" scp /home/umang/dank/cs699/Course_project_git/project-sysad-25/Database/bash_scripts/sending_submit.sh sysad@{student_ip}:/home/sysad/Desktop\n")
            file.write(f"sshpass -f \"/home/umang/dank/cs699/Course_project_git/password.txt\" ssh sysad@{student_ip} \'chmod +x /home/sysad/Desktop/sending_submit.sh\'\n")
            file.write(f"sshpass -f \"/home/umang/dank/cs699/Course_project_git/password.txt\" ssh sysad@{student_ip} \'/home/sysad/Desktop/sending_submit.sh\'\n")

        result = subprocess.run(['/home/umang/dank/cs699/Course_project_git/project-sysad-25/Database/bash_scripts/file_sending_script.sh'], check=True, capture_output=True, text=True)

        results.append(result.stdout)
        app.logger.debug(f"Submission script sent to {student_ip} for StudentID: {student['StudentID']}")
        app.logger.debug(f"Submission script output: {result.stdout}")

    return f"TA Direct Submission Script Updated and Ready to Use {results}", 200

# ===== RUN THE APP =====
if __name__ == '__main__':
    app.run(debug=True)