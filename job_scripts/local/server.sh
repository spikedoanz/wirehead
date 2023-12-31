#!/bin/bash

PORT=6379

export PATH=$PATH:/data/users1/mdoan4/wirehead/redis/redis-stable/src/

echo $HOSTNAME >&2

# Start redis
/data/users1/mdoan4/wirehead/redis/redis-stable/src/redis-server /data/users1/mdoan4/wirehead/src/utils/redis.conf >> ./log/manager_wirehead_output.log 2>> ./log/manager_wirehead_errors.log &
REDIS_PID=$!

sleep 2 

redis-cli flushall
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo $LOCAL_IP

# Start python scripts
trap 'pkill -P $$' EXIT

source /data/users1/mdoan4/wirehead/envs/wirehead_manager/bin/activate

python /data/users1/mdoan4/wirehead/src/manager.py --ip $LOCAL_IP $SLURM_ARRAY_TASK_ID #&
#python /data/users1/mdoan4/wirehead/dev_src/dataloader.py --ip $LOCAL_IP $SLURM_ARRAY_TASK_ID  

echo "Server: Terminated or Failed"
# Cleanup 
kill $REDIS_PID

wait

