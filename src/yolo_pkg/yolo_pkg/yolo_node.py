import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class YoloDetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')
        
        self.camera_topic = '/camera/image_raw'
        
        # Load Yolo Model
        self.get_logger().info('Load yolo model...')
        self.model_general = YOLO("yolov8n.pt") # Load the general model (pre-trained on COCO dataset)
        self.model_trained = YOLO("/home/w/runs/detect/train5/weights/best.pt") # Load the model trained on our custom dataset (change the path to your best.pt file)
        self.get_logger().info('Model upload!')

        self.bridge = CvBridge()

        # camera Subscriber
        self.subscription = self.create_subscription(
            Image,
            self.camera_topic,
            self.image_callback,
            10)
            
        self.publisher_ = self.create_publisher(Image, '/yolo/debug', 10)

    def image_callback(self, msg):
        try:
            # Convert from ROS format in OpenCV format (BGR)
            # Use "bgr8" because OpenCV works with Blue-Green-Red, not RGB
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Detection
            results_general = self.model_general(cv_image, verbose=False)
            results_trained = self.model_trained(cv_image, verbose=False)

            # Draw result
            annotated_frame = results_general[0].plot()
            annotated_frame = results_trained[0].plot(img=annotated_frame) # Draw the trained model's detections on top of the general model's output

            # Pop-up windows
            cv2.imshow("Robot Vacuum YOLO View", annotated_frame)
            cv2.waitKey(1)

            ros_image = self.bridge.cv2_to_imgmsg(annotated_frame, encoding="bgr8")
            self.publisher_.publish(ros_image)

        except Exception as e:
            self.get_logger().error(f'Proccessing Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = YoloDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()