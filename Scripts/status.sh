#!/bin/bash

# Usage : ./status.sh <lab_name>
# Desc : this script will output all the dead hosts

lab=$1
till=0
if [[ "$lab" == "cs101" ]]; then
	till=148
elif [[ "$lab" == "sl1" ]]; then
	till=83
elif [[ "$lab" == "sl2" ]]; then
	till=132
elif [[ "$lab" == "sl3" ]]; then
	till=44
fi

python3 .system_list.py ${lab} ${till} > .hosts

# uncomment the below comment if you want to have the data of dead hosts in a file
# echo Dead Hosts
# fping -u -f .hosts #| tee .dead
# echo ""

# echo Alive Hosts
fping -a -f .hosts > alive_hosts

#below line is for printing machine numbers
#python3 .extract_nums.py .dead
#rm .dead
rm .hosts
