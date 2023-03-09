#!/bin/sh

set -e

curl -X POST http://127.0.0.1:5000/model/naive \
     -H "Content-Type: application/json" \
     -d @example_post.json \
     --output plot.png
