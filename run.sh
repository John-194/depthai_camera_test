docker run -it --rm \
    -v $(dirname $(readlink -f $0)):/ros2_ws \
    --runtime nvidia\
    --network host \
    --privileged \
    depthai_test \
    python3 camera_test.py
