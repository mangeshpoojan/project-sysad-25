#imports
import os
from flask import Flask, request ,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import render_template
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import pandas as pd

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
            submission(Subject='software_lab', CourseCode='cs699', TestNo=1, StudentID='25m0828', SeatNo='1', Lab='sl1' ,Submitted=False),
            submission(Subject='software_lab', CourseCode='cs699', TestNo=1, StudentID='25m0829', SeatNo='2', Lab='sl1' ,Submitted=False),
            submission(Subject='software_lab', CourseCode='cs699', TestNo=1, StudentID='25m0830', SeatNo='3', Lab='sl1' ,Submitted=False),
            submission(Subject='software_lab', CourseCode='cs699', TestNo=1, StudentID='25m0831', SeatNo='4', Lab='sl1' ,Submitted=False),

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

@app.route('/submit_module', methods=['GET'])
def submit_module():
    return render_template('submit_module.html')

# ===== Serving webpage =====
@app.route('/check_lab_submissions', methods=['GET'])
def check_lab_submissions():
    # find all course codes
    course_codes = db.session.query(submission.CourseCode).distinct().all()

    #if selected TestNo in get ?course_code=cs699&test_no=1
    test_no = request.args.get('test_no')
    course_code = request.args.get('course_code')
    if test_no and course_code:
        #find the submissions for that test no and course code
        test_numbers = db.session.query(submission.TestNo).filter_by(CourseCode=course_code).distinct().all()
        submissions = db.session.query(submission).filter_by(TestNo=test_no, CourseCode=course_code).all()
        return render_template('Submission_status_page.html', course_codes=course_codes , test_numbers=test_numbers, submissions=submissions, selected_course_code=course_code, selected_test_no=test_no)

    #if contain value in get ?course_code=cs699
    course_code = request.args.get('course_code')
    if course_code:
        # get all test numbers for that course code
        test_numbers = db.session.query(submission.TestNo).filter_by(CourseCode=course_code).distinct().all()
        return render_template('Submission_status_page.html', course_codes=course_codes , test_numbers=test_numbers, selected_course_code=course_code)

    return render_template('Submission_status_page.html', course_codes=course_codes ,)

#not in use
@app.route('/check_lab_submissions_result' , methods=['POST'])
def check_lab_submissions_result():
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

# not using anymore , used in curl and update of info , used in removing student submission
@app.route('/student/submit',methods=['POST'])
def submission_student():
    data = request.form
    app.logger.debug(f"Received form data: {data}")

    if 'StudentID' not in data or 'CourseCode' not in data or 'Lab' not in data or 'Subject' not in data or 'TestNo' not in data or 'SeatNo' not in data:
        return "Missing StudentID or CourseCode or Lab or Subject or TestNo or SeatNo", 400

    if submission.query.filter_by(StudentID=data['StudentID'], CourseCode=data['CourseCode'] , Subject=data['Subject'], TestNo=data['TestNo']).count()==0:
        
        if "Submitted" in data:
            new_submission = submission(
                Subject=data['Subject'],
                CourseCode=data['CourseCode'],
                TestNo=data['TestNo'],
                StudentID=data['StudentID'],
                SeatNo=data['SeatNo'],
                Lab=data['Lab'],
                Submitted=True if data['Submitted'] == 'True' else False
            )
        else:
            new_submission = submission(
                Subject=data['Subject'],
                CourseCode=data['CourseCode'],
                TestNo=data['TestNo'],
                StudentID=data['StudentID'],
                SeatNo=data['SeatNo'],
                Lab=data['Lab'],
                Submitted=False
            )

        submitted_data = db.session.add(new_submission)
        submitted_data = single_submission_schema.dump(new_submission)
        app.logger.debug(f"New submission added: {submitted_data}")
        db.session.commit()
        return redirect(url_for('check_lab_submissions', course_code=data.get('CourseCode'), test_no=data.get('TestNo')))
        return f"Submission successful {submitted_data}", 201

    # update existing submission
    existing_data = submission.query.filter_by(StudentID=data['StudentID'], CourseCode=data['CourseCode'], TestNo=data['TestNo']).first()
    if existing_data:
        existing_data.SeatNo = data['SeatNo']
        if "Submitted" in data:
            existing_data.Submitted = True if data['Submitted'] == 'True' else False
        else:
            existing_data.Submitted = False
        existing_data.TimeStamp = datetime.now(ZoneInfo('Asia/Kolkata'))
        existing_data.Lab = data['Lab']
        db.session.commit()
        existing_data = single_submission_schema.dump(existing_data)
        app.logger.debug(f"Existing submission updated: {existing_data}")
        return redirect(url_for('check_lab_submissions', course_code=data.get('CourseCode'), test_no=data.get('TestNo')))
        return f"Submission updated {existing_data}", 200

    existing_data = single_submission_schema.dump(existing_data)
    app.logger.debug(f"Existing submission found: {existing_data}")

    if existing_data:
        return redirect(url_for('check_lab_submissions', course_code=data.get('CourseCode'), test_no=data.get('TestNo')))
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
        app.logger.debug(f"Students added successfully: {submitted_students}")
        return redirect(url_for('check_lab_submissions', course_code=data.get('CourseCode'), test_no=data.get('TestNo')))
        return f"Students added successfully: {submitted_students}", 201

    app.logger.debug("No new students were added")
    return redirect(url_for('check_lab_submissions', course_code=data.get('CourseCode'), test_no=data.get('TestNo')))
    return "Student already exists", 400

@app.route('/add_student_page')
def add_student_page():
    return render_template('add_student.html')

@app.route('/ta_direct_submit_page')
def ta_direct_submit_page():
    # find all course codes
    course_codes = db.session.query(submission.CourseCode).distinct().all()

    #if selected TestNo in get ?course_code=cs699&test_no=1
    test_no = request.args.get('test_no')
    course_code = request.args.get('course_code')

    app.logger.debug(f"TA Direct Submit Page - test_no: {test_no}, course_code: {course_code}")

    if test_no and course_code:
        app.logger.debug(f"TA Direct Submit Page - test_no: {test_no}, course_code: {course_code}")
        #find the submissions for that test no and course code
        test_numbers = db.session.query(submission.TestNo).filter_by(CourseCode=course_code).distinct().all()
        # submissions = db.session.query(submission).filter_by(TestNo=test_no, CourseCode=course_code).all()

        # app.logger.debug(f"TA Direct Submit Page - test_numbers: {test_numbers}, submissions: {submissions}")

        return render_template('ta_direct_submit.html', course_codes=course_codes , test_numbers=test_numbers,selected_course_code=course_code, selected_test_no=test_no)
    
    #if contain value in get ?course_code=cs699
    course_code = request.args.get('course_code')
    if course_code:
        # get all test numbers for that course code
        test_numbers = db.session.query(submission.TestNo).filter_by(CourseCode=course_code).distinct().all()
        return render_template('ta_direct_submit.html', course_codes=course_codes , test_numbers=test_numbers, selected_course_code=course_code)

    return render_template('ta_direct_submit.html', course_codes=course_codes)

@app.route('/ta_direct_ignore/submit', methods=['POST'])
def ta_direct_ignore():
    data = request.form
    existing_student = submission.query.filter_by(TestNo=data.get('TestNo'), CourseCode=data.get('CourseCode'), StudentID=data.get('StudentID')).first()

    # update submitted
    if existing_student:
        existing_student.Submitted=True
        existing_student.TimeStamp = datetime.now(ZoneInfo('Asia/Kolkata'))
        db.session.commit()
        app.logger.debug(f"Database updated for StudentID: {existing_student}")
        return redirect(url_for('check_lab_submissions', course_code=data.get('CourseCode'), test_no=data.get('TestNo')))
    else:
        app.logger.debug(f"No such student found: {data}")
        return redirect(url_for('check_lab_submissions', course_code=data.get('CourseCode'), test_no=data.get('TestNo')))
        return f"No such student{data}"


@app.route('/ta_direct_submit_page/submit',methods=['POST'])
def ta_direct_submit():
    data = request.form
    app.logger.debug(f"Received form data: {data}")
    single_student=0
    if 'StudentID' in data:
        single_student = data['StudentID']
        app.logger.debug(single_student)

    if not single_student:
        submissions_list = submission.query.filter_by(TestNo=data.get('TestNo'), CourseCode=data.get('CourseCode')).all()
        submissions_list_dumped = multi_submission_schema.dump(submissions_list)
        app.logger.debug(f"Query result many: {submissions_list_dumped}")
    else:
        submissions_list = submission.query.filter_by(TestNo=data.get('TestNo'), CourseCode=data.get('CourseCode'), StudentID=single_student).all()
        submissions_list_dumped = multi_submission_schema.dump(submissions_list)
        app.logger.debug(f"Query result single: {submissions_list_dumped}")

    results = []
    result = {}
    for student in submissions_list_dumped:
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
            file.write(f"DESTINATION_PATH=/home/cs683/submissions/{data['CourseCode']}/{data['TestNo']}\n")
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
        
        #creating folder structure
        try:
            output=subprocess.run(['sshpass', '-p', 'sahilunagar', 'ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'ConnectTimeout=3', f'cs683@10.9.100.47', f'mkdir -p /home/cs683/submissions/{data["CourseCode"]}/{data["TestNo"]}'], check=True)
            app.logger.debug(f"Output of directory creation: {output}")
        except subprocess.CalledProcessError as e:
            app.logger.debug(f"Directory creation failed with error: {e}")
            return f"Directory creation failed for StudentID: {student['StudentID']}", 500

        with open("bash_scripts/file_sending_script.sh", "w") as file:
            file.write("#!/bin/bash\n")
            file.write(f"sshpass -f \"/home/umang/dank/cs699/Course_project_git/password.txt\" scp -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o UserKnownHostsFile=/dev/null /home/umang/dank/cs699/Course_project_git/project-sysad-25/Database/bash_scripts/sending_submit.sh sysad@{student_ip}:/home/sysad/Desktop\n")
            file.write(f"sshpass -f \"/home/umang/dank/cs699/Course_project_git/password.txt\" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 sysad@{student_ip} \'chmod +x /home/sysad/Desktop/sending_submit.sh\'\n")
            file.write(f"sshpass -f \"/home/umang/dank/cs699/Course_project_git/password.txt\" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o UserKnownHostsFile=/dev/null sysad@{student_ip} \'/home/sysad/Desktop/sending_submit.sh\'\n")
        try:
            result = subprocess.run(['/home/umang/dank/cs699/Course_project_git/project-sysad-25/Database/bash_scripts/file_sending_script.sh'], check=True, capture_output=True, text=True)
        

            if "successfully submitted" in result.stdout:
                app.logger.info(f"Submission successful for StudentID: {student['StudentID']}")
                #update db
                existing_data = submission.query.filter_by(StudentID=student['StudentID'], CourseCode=data.get('CourseCode'), TestNo=data.get('TestNo')).first()
                if existing_data:
                    existing_data.Submitted = True
                    existing_data.TimeStamp = datetime.now(ZoneInfo('Asia/Kolkata'))
                    db.session.commit()
                    app.logger.debug(f"Database updated for StudentID: {student['StudentID']}")
            else:
                app.logger.debug(f"unsuccessful{student}")
                app.logger.debug(f'''{type(result.stdout)}---{result.stdout.find("successfully submitted")}''')

 
            results.append(result.stdout)
            app.logger.debug(f"Submission script sent to {student_ip} for StudentID: {student['StudentID']}")
            app.logger.debug(f"Submission script output: {result.stdout} ")
        
        except subprocess.CalledProcessError as e:
            app.logger.debug(f"Command failed with error: {e}")

    # if not single_student:
    return redirect(url_for('check_lab_submissions', course_code=data.get('CourseCode'), test_no=data.get('TestNo')))
    
    return f"TA Direct Submission Script Updated and Ready to Use {results}", 200


#update student info new page
@app.route('/update_student_info_page' , methods=['GET'])
def update_student_info_page():
    #of format ?course_code=cs683&test_no=1studentid=25m0001
    course_code = request.args.get('course_code')
    test_no = request.args.get('test_no')
    student_id = request.args.get('studentid')
    app.logger.debug(f"Update Student Info Page - course_code: {course_code}, test_no: {test_no}, student_id: {student_id}")

    if course_code and test_no and student_id:
        # find the submission for that student
        submission_data = submission.query.filter_by(TestNo=test_no, CourseCode=course_code, StudentID=student_id).first()
        if submission_data:
            submission_data_serialized = single_submission_schema.dump(submission_data)
            # return f"Submission data found: {submission_data_serialized}"
            app.logger.debug(f"Submission data found: {submission_data_serialized}")
            return render_template('update_student_info.html', student=submission_data_serialized)
        else:
            app.logger.debug(f"No submission found for StudentID: {student_id}")
            return "No submission found for the given StudentID", 404

    return render_template('update_student_info.html')

#single person submit merged with multiple person submit

@app.route('/bulk_add_students_page')
def bulk_add_students_page():
    return render_template('bulk_add_students.html')
 
@app.route('/bulk_add_students_page/submit', methods=['POST'])
def bulk_add_students():
    data = request.form
    app.logger.debug(f"Received form data: {data}")

    if 'excel_file' not in request.files:
        return "No file part", 400

    file = request.files['excel_file']
    if file.filename == '':
        return "No selected file", 400

    #excel file processing
    if file:
        df = pd.read_excel(file)
        app.logger.debug(f"Excel file columns: {df.columns.tolist()}")
        app.logger.debug(f"Excel file data:\n{df}")
        submitted_students = []
        for index, row in df.iterrows():
            student_id = str(row['StudentID']).strip()
            seat_no = str(row['SeatNo']).strip()
            lab = str(row['Lab']).strip()

            if submission.query.filter_by(StudentID=student_id, CourseCode=data['CourseCode'] , Subject=data['Subject'], TestNo=data['TestNo']).count()==0:
                new_submission = submission(
                    Subject=data['Subject'],
                    CourseCode=data['CourseCode'],
                    TestNo=data['TestNo'],
                    StudentID=student_id,
                    SeatNo=seat_no,
                    Lab=lab,
                    Submitted=False
                )
                db.session.add(new_submission)
                db.session.commit() 
                new_submission_serialized = single_submission_schema.dump(new_submission)
                app.logger.debug(f"New student added: {new_submission_serialized}")
                submitted_students.append(new_submission_serialized)
            else:
                app.logger.debug(f"Student already exists: {student_id}")
                existing_student = submission.query.filter_by(StudentID=student_id, CourseCode=data['CourseCode'] , Subject=data['Subject'], TestNo=data['TestNo']).first()
                #update existing student info
                existing_student.SeatNo = seat_no
                existing_student.Lab = lab
                db.session.commit()
                existing_student_serialized = single_submission_schema.dump(existing_student)
                app.logger.debug(f"Existing student data: {existing_student_serialized}")

        if submitted_students:
            return redirect(url_for('check_lab_submissions', course_code=data.get('CourseCode'), test_no=data.get('TestNo')))
            # return f"Students added successfully: {submitted_students}", 201

    return "No new students were added", 400

# ===== RUN THE APP =====
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
