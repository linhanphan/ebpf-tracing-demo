#!/bin/bash
for i in $(seq 1 10)
do
  curl myservice:8080/random
  sleep 1
done
