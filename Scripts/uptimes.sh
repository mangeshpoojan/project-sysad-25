#!/bin/bash

password="$(cat shadow)"

#OUTFILE="disk_space_$(date +%F_%H%M%S).txt"
OUTFILE="uptimes.txt"
host=$2
lab=$1
remote="sl${lab}-${host}.cse.iitb.ac.in"

result=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=13 sysad@"$remote" "uptime -p | awk '{print \$2, \$3, \$4, \$5, \$6, \$7}'")

echo $result
echo "$lab-$host $result"  >> "$OUTFILE"
echo "Saved results in $OUTFILE"

