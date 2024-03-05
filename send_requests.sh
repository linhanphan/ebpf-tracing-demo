#!/bin/bash
for i in {1..10}
do
  curl myservice:8080/random
done
