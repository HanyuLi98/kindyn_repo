#! /usr/bin/env python
import math
import sys
import json
import matplotlib.pyplot as plt

import rospy
from roboy_middleware_msgs.srv import InverseKinematics
from geometry_msgs.msg import Pose, Point, Quaternion

JSON_FILENAME = "captured_trajectory.json"

###############################
###   MEASURED PARAMETERS   ###
###############################

PEDAL_CENTER_OFFSET_X = 0.20421
PEDAL_CENTER_OFFSET_Y = -0.00062
PEDAL_CENTER_OFFSET_Z = 0.2101

PEDAL_RADIUS = 0.16924  # [millimeters]

RIGHT_LEG_OFFSET_Y = 0.2095
LEFT_LEG_OFFSET_Y = -0.13815

##############################
###   UTILITY FUNCTIONS   ###
##############################

def getPedalPositions(numSamples):
    # Format: [[pedal_angle_1, x, y, z], [pedal_angle_2, x, y, z], ...]
    capturedPositions = []
    angularStep = 2.0*math.pi/numSamples
    for sampleIterator in range(numSamples+1):
        thisPedalAngle = sampleIterator*angularStep
        thisXVal = PEDAL_CENTER_OFFSET_X + math.cos(thisPedalAngle)*PEDAL_RADIUS
        thisYVal = PEDAL_CENTER_OFFSET_Y
        thisZVal = PEDAL_CENTER_OFFSET_Z + math.sin(thisPedalAngle)*PEDAL_RADIUS
        capturedPositions.append([thisPedalAngle, thisXVal, thisYVal, thisZVal])

    return capturedPositions


def plotPedalTrajectories():
    numSamples = []
    if len(sys.argv) > 1:
        for argIterator in range(1, len(sys.argv)):
            numSamples.append(int(sys.argv[argIterator]))

    plt.title('Pedal trajectory estimation by number of intermediate points')

    for thisSample in numSamples:
        capturedPositions = getPedalPositions(thisSample)
        x_values = []
        z_values = []
        for pointIterator in capturedPositions:
            x_values.append(pointIterator[1])
            z_values.append(pointIterator[3])
        plt.plot(x_values, z_values,label=str(thisSample))
    plt.legend()
    plt.show()

def plotEverything(numSamples, jointAngleDict):

    plt.figure(1)
    plt.title('Pedal trajectory planned and ik result')
    capturedPositions = getPedalPositions(numSamples)
    x_values = []
    z_values = []
    for pointIterator in capturedPositions:
        x_values.append(pointIterator[1])
        z_values.append(pointIterator[3])
    plt.plot(x_values, z_values,label="Ideal")
    for pointIter in range(jointAngleDict["num_points"]):
        if "point_"+str(pointIter) in jointAngleDict:
            if "Pedal" in jointAngleDict["point_"+str(pointIter)]:
                plt.plot(jointAngleDict["point_"+str(pointIter)]["Pedal"][0], jointAngleDict["point_"+str(pointIter)]["Pedal"][1], 'rs',label="IK recorded")

    
    plt.figure(2)
    plt.title('Hip positions')
    x_values = []
    z_values = []
    for pointIter in range(jointAngleDict["num_points"]):
        if "point_"+str(pointIter) in jointAngleDict:
            if "Hip" in jointAngleDict["point_"+str(pointIter)]:
                x_values.append(pointIter)
                z_values.append(jointAngleDict["point_"+str(pointIter)]["Hip"])
    plt.plot(x_values, z_values)

    plt.figure(3)
    plt.title('Knee positions')
    x_values = []
    z_values = []
    for pointIter in range(jointAngleDict["num_points"]):
        if "point_"+str(pointIter) in jointAngleDict:
            if "Knee" in jointAngleDict["point_"+str(pointIter)]:
                x_values.append(pointIter)
                z_values.append(jointAngleDict["point_"+str(pointIter)]["Knee"])
    plt.plot(x_values, z_values)

    plt.figure(4)
    plt.title('Ankle positions')
    x_values = []
    z_values = []
    for pointIter in range(jointAngleDict["num_points"]):
        if "point_"+str(pointIter) in jointAngleDict:
            if "Ankle" in jointAngleDict["point_"+str(pointIter)]:
                x_values.append(pointIter)
                z_values.append(jointAngleDict["point_"+str(pointIter)]["Ankle"])
    plt.plot(x_values, z_values)

    plt.show()



def inverse_kinematics_client(endeffector, frame, x, y, z):
    rospy.wait_for_service('ik')
    try:
        ik_srv = rospy.ServiceProxy('ik', InverseKinematics)
        requested_position = Point(x, y, z)
        requested_pose = Pose(position=requested_position)
        requested_ik_type = 1  #Position only
        ik_result = ik_srv(endeffector, requested_ik_type, frame, requested_pose)

        jointDict = {}
        for thisJoint in range(len(ik_result.angles)):
            jointDict[ik_result.joint_names[thisJoint]] = ik_result.angles[thisJoint]

        return jointDict

    except rospy.ServiceException, e:
        print "Service call failed: %s"%e


################
###   MAIN   ###
################

def main():

    if len(sys.argv) > 1:
        num_requested_points = int(sys.argv[1])
    else:
        num_requested_points = 72

    #plotPedalTrajectories()

    capturedPositions = getPedalPositions(num_points)

    endeffector_right = "right_leg"
    frame_right = "right_leg"
    y_offset_right = RIGHT_LEG_OFFSET_Y

    endeffector_left = "left_leg"
    frame_left = "left_leg"
    y_offset_left = LEFT_LEG_OFFSET_Y

    jointAngleDict = {}
    jointAngleDict["num_points"] = num_requested_points

    for pointIter in range(num_points):
        thisX = capturedPositions[pointIter][1]
        thisZ = capturedPositions[pointIter][3]
        thisPedalAngle = = capturedPositions[pointIter][0]
        jointAngleResult_right = inverse_kinematics_client(endeffector_right, frame_right, thisX, y_offset_right, thisZ)
        jointAngleResult_left = inverse_kinematics_client(endeffector_left, frame_left, thisX, y_offset_left, thisZ)
        if (jointAngleResult_right and jointAngleResult_left):
    		jointAngleDict["point_"+str(pointIter)] = {}
        	jointAngleDict["point_"+str(pointIter)]["Left"] = {}
        	jointAngleDict["point_"+str(pointIter)]["Right"] = {}
    		jointAngleDict["point_"+str(pointIter)]["Left"]["Pedal"] = [thisX, thisZ]
            jointAngleDict["point_"+str(pointIter)]["Left"]["Pedal_angle"] = thisPedalAngle
    		jointAngleDict["point_"+str(pointIter)]["Left"]["Hip"] = jointAngleResult_left["joint_hip_left"]
    		jointAngleDict["point_"+str(pointIter)]["Left"]["Knee"] = jointAngleResult_left["joint_knee_left"]
    		jointAngleDict["point_"+str(pointIter)]["Left"]["Ankle"] = jointAngleResult_left["joint_foot_left"]
        	jointAngleDict["point_"+str(pointIter)]["Right"]["Pedal"] = [thisX, thisZ]
            jointAngleDict["point_"+str(pointIter)]["Left"]["Pedal_angle"] = thisPedalAngle
    		jointAngleDict["point_"+str(pointIter)]["Right"]["Hip"] = jointAngleResult_right["joint_hip_right"]
    		jointAngleDict["point_"+str(pointIter)]["Right"]["Knee"] = jointAngleResult_right["joint_knee_right"]
    		jointAngleDict["point_"+str(pointIter)]["Right"]["Ankle"] = jointAngleResult_right["joint_foot_right"]
        else:
            jointAngleDict["num_points"] = jointAngleDict["num_points"] - 1

    #print(jointAngleDict)
    with open(JSON_FILENAME, "w") as write_file:
        json.dump(jointAngleDict, write_file, indent=4, sort_keys=True)

    plotEverything(jointAngleDict["num_points"], jointAngleDict)

    return 1

if __name__ == '__main__':
    main()
