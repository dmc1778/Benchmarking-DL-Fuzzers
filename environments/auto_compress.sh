#!/bin/sh

while true
do
  echo "Auto compression started..."
  tar czf fuzzgpt_results.tar.gz fewshot/
  echo "Auto compression finished. Please wait for 60 seconds for the next round."
  sleep 60
done