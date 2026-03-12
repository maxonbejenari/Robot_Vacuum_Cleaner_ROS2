import rclpy # ROS2 Python client library
from rclpy.node import Node # Base class for ROS2 nodes
from sensor_msgs.msg import Image # ROS2 message type for images
from cv_bridge import CvBridge # OpenCV bridge for ROS2
import cv2 # OpenCV library for image processing
import os # Working with files and paths from Linux

class DataCollectorNode(Node):
    def __init__(self):
        super().__init__('data_collector_node')
        
        self.camera_topic = '/camera/image_raw' # Topic wich we will listen to
        self.save_directory = os.path.expanduser('~/dataset_gazebo/images') # Directory where we will save the images
        self.save_interval = 5.0 # Save an image every 5 seconds
        self.image_counter = 0 # Counter for naming the images
        
        # Create the directory if it doesn't exist
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
        
        # Initialize CvBridge
        self.bridge = CvBridge()
        
        # Create Subscriber to the camera topic
        self.subscription = self.create_subscription(
            Image,
            self.camera_topic,
            self.image_callback,
            10 # QoS (Quality of Service) / Queue size
        )
        
        self.timer = self.create_timer(self.save_interval, self.timer_callback) # Timer to save images at regular intervals
        self.latest_image = None
        self.get_logger().info('Data Collector Node has been started...')
        
        
    # Function called when a new image is received
    def image_callback(self, msg):
        try:
            self.latest_cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8') # Convert ROS image to OpenCV format
        except Exception as e:
            self.get_logger().error(f'Error converting image: {e}')
    
    
    def timer_callback(self):
        if self.latest_cv_image is not None:
            # Create name for the new image
            #zfill(4) adds leading zeros to the number, so we get image_0001.jpg, image_0002.jpg, etc.
            filename = f"image_{str(self.image_counter).zfill(4)}.jpg"
            filepath = os.path.join(self.save_directory, filename)
            
            # OpenCV function to save the image on hard disk
            cv2.imwrite(filepath, self.latest_cv_image)
            
            self.get_logger().info(f'Saved image: {filepath}')
            self.image_counter += 1


def main(args=None):
   rclpy.init(args=args)
   node = DataCollectorNode()
   
   try:
       rclpy.spin(node)
   except KeyboardInterrupt:
       node.get_logger().info('Data Collector Node is shutting down...')
   finally:
       node.destroy_node()
       rclpy.shutdown()

if __name__ == '__main__':
    main()
        