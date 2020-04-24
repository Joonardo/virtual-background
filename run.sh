#!/bin/sh

sh -c "trap 'kill 0' SIGINT; cd partitioner && npm run start" &
P1=$!

sh -c "trap 'kill 0' SIGINT; sleep 5 && cd webcam && source ./bin/activate && python -m webcam" &
P2=$!

wait $P1 $P2
