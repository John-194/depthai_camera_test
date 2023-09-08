#!/bin/bash
set -e

ros_env_setup="${ROS_ROOT}/install/setup.bash"
echo "sourcing $ros_env_setup"
source "$ros_env_setup"

echo "exporting PYTHONPATH=/usr/local/lib/python3.8/site-packages/:$PYTHONPATH"
export PYTHONPATH=/usr/local/lib/python3.8/site-packages/:$PYTHONPATH

echo "exporting LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

echo "exporting OPENBLAS_CORETYPE=ARMV8"
export OPENBLAS_CORETYPE=ARMV8

echo ""
exec "$@"
