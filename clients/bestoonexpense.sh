#!/bin/bash

TOKEN=1234567
BASE_URL=http://127.0.0.1:9000

curl --data "token=$TOKEN&amount=$1&text=$2" $BASE_ULR/submit/expense/
