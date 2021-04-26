import rospy
from sensor_msgs.msg import JointState
from roboy_middleware_msgs.msg import MotorCommand
import numpy as np
from std_srvs.srv import Trigger
from std_msgs.msg import Empty

rospy.init_node("handshake")
topic_root = '/roboy/brain/control/'
publisher = rospy.Publisher(topic_root + "joint_targets", JointState, queue_size=1)
msg = JointState()
hand_msg = MotorCommand()
hand_msg.global_id = [42,42,44,45]
motorcmd_pub = rospy.Publisher(topic_root + "middleware/MotorCommand", MotorCommand, queue_size=1)
rate = rospy.Rate(100)

def close_hand():
    hand_msg.setpoint = [900]*len(hand_msg.global_id)
    motorcmd_pub.publish(hand_msg)

def open_hand():
    hand_msg.setpoint = [0]*len(hand_msg.global_id)
    motorcmd_pub.publish(hand_msg)

def move_fingers(right_hand = True, targets = [0,0,0,0]):
    """
    :param target: array of finger target values between 0 (open hand) and 800 (closed hand)
    lr: "left" or "right"
    left_ids = [38, 39, 40, 41]
    right_ids = [42, 43, 44, 45]
    """

    if right_hand:
        hand_msg.global_id = [42, 42, 44, 45]

    else:
        hand_msg.global_id = [38, 39, 40, 41]

    hand_msg.setpoint = [i*800 for i in targets]
    motorcmd_pub.publish(hand_msg)
    rospy.sleep(0.07)

def move_fingers_simultaneous(right_hand = True):
    # hand finger moving test all fingers move the same
    ranges = [0, 1]
    samples = 101

    for i in range(2):
        if not i%2:
            print(right_hand, "close")
            target_value = np.linspace(ranges[0], ranges[1], samples)  # start with 0 (open) -> 1 (close)
            for pos in target_value:
                targets = [pos] * len(hand_msg.global_id)  # put the current pos value in a 4-element list
                move_fingers(right_hand, targets)
        else:
            print(right_hand, "open")
            target_value = np.linspace(ranges[1], ranges[0], samples)  # start with 1 -> 0
            for pos in target_value:
                targets = [pos] * len(hand_msg.global_id)
                move_fingers(right_hand, targets)

def move_pointer_finger(right_hand = True):
    ranges = [0, 1]
    samples = 101

    for i in range(2):
        if not i%2:
            print(right_hand, "close")
            target_value = np.linspace(ranges[0], ranges[1], samples) # start with 0 (open) -> 1 (close)
            for pos in target_value:
                targets = [0, pos, 0, 0] # put the current pos value in a 4-element list TODO: what is the pointer finger
                move_fingers(right_hand, targets)
        else:
            print(right_hand, "open")
            target_value = np.linspace(ranges[1], ranges[0], samples) # start with 1 -> 0
            for pos in target_value:
                targets = [0, pos, 0 , 0]
                move_fingers(right_hand, targets)

move_pointer_finger(right_hand = True)
#move_fingers_simultaneous(right_hand = True)