#!/bin/bash
for i in $(seq 1 10)
do
  curl 172.18.0.1:8080/random
  sleep 1
done
