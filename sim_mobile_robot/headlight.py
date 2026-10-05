import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool # Request: bool data | Response: bool success, string message

class HeadlightService(Node):

    def __init__(self):
        super().__init__('headlight_service')
        
        # Create a Service Server
        self.srv = self.create_service(SetBool, '/toggle_headlights', self.handle_light_toggle)
        self.lights_on = False
        self.get_logger().info('Headlight Service Server Ready.')

    def handle_light_toggle(self, request, response):
        self.lights_on = request.data # True = turn on, False = turn off
        
        if self.lights_on:
            response.success = True
            response.message = "Headlights switched ON"
            self.get_logger().info("Headlights turned ON")
        else:
            response.success = True
            response.message = "Headlights switched OFF"
            self.get_logger().info("Headlights turned OFF")
            
        return response

def main(args=None):
    rclpy.init(args=args)
    node = HeadlightService()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
