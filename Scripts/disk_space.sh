#!/bin/bash

password="$(cat shadow)"

#OUTFILE="disk_space_$(date +%F_%H%M%S).txt"
OUTFILE="disk_space.txt"
lab=$1
host=$2
remote="${lab}-${host}.cse.iitb.ac.in"

result=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=13 sysad@"$remote" "df -h / | awk 'NR==2 {print \$2, \$3, \$4, \$5}'" 2>/dev/null)

echo "$lab-$host $result" # >> "$OUTFILE"
