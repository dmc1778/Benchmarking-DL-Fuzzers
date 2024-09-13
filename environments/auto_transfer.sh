#!/bin/sh

while true
do
  echo "Auto transfer from remote machine to the local machine started..."
  scp -i ~/.ssh/tosem.pem ubuntu@104.171.202.48:/home/ubuntu/code-atlasfuzz/fuzzgpt_results.tar.gz /home/nima/
  echo "Auto transfer finished. Please wait for 60 minutes for the next round."
  sleep 60
done