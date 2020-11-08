#!/bin/bash
cd autonomous_hegician/
echo $DB_URL
aea -s install
aea -s run
