#science-mapping

This package contains the science_mapping node. The node receives a GP belief space (formatted as a three-dimensional array) from the GaussianProcess package. Eventually, we hope to receive this as ROS input. The node will generate and return a pointcloud of the greatest points of interest.

### Inputs:
- Bool /semaphore: a signal from motion planning to find a new set of points to travel to

### Outputs:
- PointCloud /possible_points: a set of possible points of interest, along with their value

The file GaussianProcess.py is copied with minor modification from the Gaussian Process team's repository, in order to be able to import the Gaussian Process package.
