#! /usr/bin/env python

import pathlib

import numpy as np
np.set_printoptions(suppress=True, precision=2)

import libodri_control_interface_pywrap as oci


robot = oci.robot_from_yaml_file("config_solo12.yaml")

# Initialize the communication and the session.
robot.start()
robot.wait_until_ready()

# Calibrate the robot if needed.
robot.run_calibration()

robot.parse_sensor_data()
init_imu_attitude = robot.imu.attitude_euler.copy()

des_pos = np.zeros(12)

c = 0
dt = 0.001
calibration_done = False
while not robot.is_timeout:
    robot.parse_sensor_data()

    imu_attitude = robot.imu.attitude_euler
    positions = robot.joints.positions
    velocities = robot.joints.velocities

    des_pos[:] = imu_attitude[2] - init_imu_attitude[2]
    torques = 5.0 * (des_pos - positions) - 0.1 * velocities
    robot.joints.set_torques(torques)

    if c % 2000 == 0:
        print("IMU attitude:", imu_attitude)
        print("joint pos:   ", positions)
        print("joint vel:   ", velocities)
        print("torques:     ", torques)
        robot.robot_interface.PrintStats()

    robot.send_command_and_wait_end_of_cycle()
    c += 1
