FROM dustynv/ros:humble-desktop-l4t-r35.3.1
ARG DEBIAN_FRONTEND=noninteractive

# install Depthai
RUN pip install --extra-index-url https://artifacts.luxonis.com/artifactory/luxonis-python-snapshot-local/ depthai

# replace entrypoint
RUN rm /ros_entrypoint.sh && mkdir /ros2_ws && mkdir /ros2_ws/source && touch /ros2_ws/source/setup.bash
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    sed -i \
      's/ros_env_setup="\/opt\/ros\/$ROS_DISTRO\/setup.bash"/ros_env_setup="${ROS_ROOT}\/install\/setup.bash"/g' \
      /entrypoint.sh && \
    echo 'source ${ROS_ROOT}/install/setup.bash' >> /root/.bashrc
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
WORKDIR /ros2_ws
