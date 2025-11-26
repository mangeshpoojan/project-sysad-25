#!/bin/bash
DIR="/home/sysad/Desktop/submission_25m0001"
SESSION=sysad
DESTINATION_PATH=/home/cs683/submissions/cs699/8
COURSE_CODE=cs699
TEST_NO=8
ROLLNO=25m0001
FILENAME=/home/sysad/Desktop/sl1-1_submission_25m0001.tar.gz

if [ -d "$DIR" ]; then
        if [ "$(ls -A $DIR)" ]; then
                rm -f $FILENAME
                 # List all files, folders, and subfolders in $DIR with sizes and timestamps
                echo "[$COURSE_CODE] Files that are checked are:"
                        echo "Files                    |  Size (bytes) | Timestamp"
                find $DIR -type f -exec stat -c "%n %s %Y" {} \; | awk -v dir="$DIR" '{sub("^" dir "/", ""); rounded_seconds = int($3 + 0.5); printf "%-24s | %13s | %s %s:%s\n", $1, $2, strftime("%d %b %Y", $3), strftime("%H", rounded_seconds), strftime("%M:%S", rounded_seconds); }'  > /home/sysad/find_results.txt 
                cat /home/$SESSION/find_results.txt 
                        # find $DIR -type d -exec stat -c "%n %s %y" {} \; | awk '{printf "%-20s | %13s | %s %s\n", system("basename "$1), $2, $3, $4}'
                echo "$(date '+%Y-%m-%d %H:%M:%S')  ::  Roll: ${roll} " > /home/$SESSION/Desktop/submission_${roll}/submission_status.txt
                tar -cvzf $FILENAME -C /home/$SESSION/Desktop/ submission_${roll} >  /dev/null 2>&1
                
        else
                echo "submission_${roll} is empty !! Please add your programs  to the submission_${roll} folder in Desktop directory"
                exit 0
        fi
else
        echo "Cannot find submission folder!! It should be present in the Desktop folder and named as submission_${roll}"
        exit 0
fi

SOURCE_DIR = "/home/$SESSION/Desktop"
cd ${SOURCE_DIR}

rollno=$(ls | grep "_submission_" | sed -n 's/^.*\([0-9]\{2\}[a-zA-Z][0-9]\{4\}\).*$/\1/p')

echo $rollno

host_parts=$(hostname | sed 's/-/ /')
read lab seat_number <<< "$host_parts"

echo "Lab Variable: $lab"
echo "Seat Number Variable: $seat_number"

if [ -f "$FILENAME" ]
then
    echo "Files that will be submitted are:"
    echo "Files                    |  Size (bytes) | Timestamp"
    cat /home/sysad/find_results.txt 
    sshpass -p "sahilunagar" scp -o StrictHostKeyChecking=no -o ConnectTimeout=10 $FILENAME cs683@10.9.100.47:$DESTINATION_PATH
    if [ $? -eq 0 ]
    then
      echo "successfully submitted !!"
      # curl -d "StudentID=$rollno&CourseCode=$course_code&Lab=$lab&Subject=$subject&TestNo=$test_no&SeatNo=$seat_number&Submitted=True" -X POST http://localhost:5000/student/submit
    else
      echo "please retry submissioni!!"
    fi
else
  echo "Please run check first!!"
fi