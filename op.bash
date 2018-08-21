#!/bin/bash

# Clients command
basepath=$(pwd)

echo bitcoin-cli -datadir=$basepath/log/1 getbalance

