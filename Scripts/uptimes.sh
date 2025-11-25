#!/bin/bash

password="$(cat .shadow)"

OUTFILE="uptimes.txt"
lab=$1
host=$2
remote="${lab}-${host}.cse.iitb.ac.in"

result=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=13 sysad@"$remote" "uptime -p | awk '{print \$2, \$3, \$4, \$5, \$6, \$7}'")

echo "$lab-$host $result" # >> "$OUTFILE"

