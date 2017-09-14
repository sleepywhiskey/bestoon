#!/bin/bash

source config.sh

curl --data "token=$TOKEN&amount=$1&text=$2" http://localhost:9000/submit/income/
