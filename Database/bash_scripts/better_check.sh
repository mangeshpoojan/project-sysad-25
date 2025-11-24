
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

