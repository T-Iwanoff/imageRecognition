
from image_recognition.analyse_image import analyse_image
from connection_test import *

# IMAGE, VIDEO, CAMERA or ROBOT
# analyse_image(path='Media/Video/MovingBalls.mp4', media='VIDEO')

analyse_image(path='Media/Video/MovingBalls.mp4', media='VIDEO', mac_camera=False)

# analyse_image(path='Media/Image/Bold2-165-84.5.jpg', media='IMAGE')

# analyse_image(media='MAC_CAMERA')

# analyse_image(path='Media/Image/Cluster2.jpg', media='IMAGE')
