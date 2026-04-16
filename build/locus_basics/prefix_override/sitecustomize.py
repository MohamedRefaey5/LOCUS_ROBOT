import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/phoenix/ros_projects/LOCUS/install/locus_basics'
