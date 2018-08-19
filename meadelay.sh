#!/bin/bash

./initial.sh

sleep 2

./service.sh

sleep 65

echo "start measure delay of transactions..."

./delaymeasure.py

echo "finish measurement."

sleep 2

./endservice.sh

sleep 1

./stop.bash
