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