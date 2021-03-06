#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String, Bool
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import PointCloud, ChannelFloat32
from geometry_msgs.msg import Point
import numpy as np
import imp
from copy import deepcopy

# From Gaussian Team
#GaussianProcess = imp.load_source("GaussianProcess", '/home/vpreston/catkin_ws/src/cogrob-challenge/science_mapping/scripts/Gaussian_Processes_Sampling/GaussianProcess.py')
# import util -  not sure if we need this
import GaussianProcess

#NOTE! If you want to publish to /update_points, type the following in a terminal:
# rostopic pub -1 /semaphore std_msgs/Bool -- 'True'

class ScienceMapping():
    def __init__(self):
        self.sub = rospy.Subscriber("/semaphore", Bool, self.getmap_cb, queue_size=10)
        # self.sub = rospy.Subscriber("/map", OccupancyGrid, self.slam_map_cb, queue_size=10 )
        self.pub = rospy.Publisher("/possible_points", PointCloud, queue_size=10)
        self.num = 10
        # rospy.init_node('science_mapping')
        # rate = rospy.Rate(5)
        # while not rospy.is_shutdown():
        #     self.getmap_cb(True)
        #     rate.sleep()
        self.map_msg = None
        self.beta = rospy.get_param('science_mapping/beta')


    def slam_map_cb(self, msg):
    	self.map_msg = msg

    
    def getmap_cb(self, val):
        if val.data == True:
            science = [(6, 1), (3, 1)]
            m = GaussianProcess.get_image_map()

            entropy = np.sum(- m * np.log2(m), axis=2)

            # Find the max entropy value
            entropyMax = np.amax(entropy)

            # Calculate mean value
            means = np.sum(m * np.array(science)[:,0], axis=2)

            # Find max means value
            meansMax = np.amax(means)
            
            # Trade-off function
            rewards = np.zeros((m.shape[0],m.shape[1]))
            rewards.flatten()
            rewards = []
            
            for i in range(0,m.shape[0]):
                for j in range(0,m.shape[1]):
                    reward = (1 - self.beta)*(means[i,j]/meansMax) + self.beta*(entropy[i,j]/entropyMax)

                    rewardIdx = [i, j, reward]
                    rewards.append(rewardIdx)

            # # Rank rewards from most to least
            sortedRewards = sorted(rewards, key= lambda x: x[2], reverse=True)
            # print sortedRewards[0:10]
            rospy.loginfo("Rewards generated")

            # Make the point cloud to publish
            # sortedRewards = self.check_feasibility(sortedRewards)
            self.pub.publish(self.create_point_cloud(sortedRewards))

        else:
            pass

    def check_feasibility(self, rewards):
    	r = deepcopy(rewards)
        g = []
    	for element in r:
		px = element[0]/self.map_msg.info.resolution - self.offset_x
		py = element[1]/self.map_msg.info.resolution - self.offset_y

            	x_query = [px+(i-2) for i in range(0,4)]
            	y_query = [py+(i-2) for i in range(0,4)]

        	adjusted_x = []
            	adjusted_y = []

		for i,x in enumerate(x_query):
			for j,y in enumerate(y_query):
			    if self.map_msg.data[x,y] >= 40. or self.map_msg.data[x,y]==-1.:
				adjusted_x.append(-(x-px))
				adjusted_y.append(-(y-px))
			    else:
				pass
			if len(adjusted_x) != 0 and len(adjusted_y) != 0:
			    if element[0]+np.mean(adjusted_x) == element[0] and element[1]+np.mean(adjusted_y) == element[1]:
				pass
			    else:
				g.append([element[0]+np.mean(adjusted_x), element[1]+np.mean(adjusted_y)])
			else:
			    g.append([element[0], element[1]])
        return g


    def create_point_cloud(self, rewards):
    	# get map information fist
    	# x = self.map_msg.info.origin.orientation.x
    	# y = self.map_msg.info.origin.orientation.y
    	# z = self.map_msg.info.origin.orientation.z
    	# w = self.map_msg.info.origin.orientation.w

    	# roll, pitch, yaw = euler_from_quaternion((x,y,z,w))

    	# offset_x = self.map_msg.info.origin.position.x
    	# offset_y = self.map_msg.info.origin.position.y


    	c = PointCloud()
    	c.header.seq = 1
    	c.header.stamp = rospy.Time.now()
    	c.header.frame_id = '/map'

    	c.points = []

    	channel = ChannelFloat32()
    	channel.name = "Values"
    	channel.values = []

    	c.channels = [channel]

    	for element in rewards[0:self.num-1]:
    		p = Point()
    		x = element[0]#(element[0]*np.cos(yaw) + element[1]*np.sin(yaw))*self.map_msg.info.resolution + offset_x
    		y = element[1]#(-element[0]*np.sin(yaw) + element[1]*np.cos(yaw))*self.map_msg.info.resolution + offset_y
    		val = element[2]

    		p.x = x
    		p.y = y
    		c.points.append(p)
    		channel.values.append(val)

    	return c

        #TODO make the 10 a parameter
        #TODO run evaluations on the GP Team stuff (confirm science points look good)


if __name__ == '__main__':
    try:
    	rospy.init_node('science_mapping')
        active = ScienceMapping()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
