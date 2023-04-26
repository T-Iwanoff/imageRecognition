from run_image_analysis import run_image_analysis
import os

# change this to the path of your image directory
image_dir = 'Media\Image'
image_paths = []

for filename in os.listdir(image_dir):
    # or any other image file extensions you have
    if (filename.endswith('.jpg') or filename.endswith('.png')) and filename.startswith('Bold'):
        image_paths.append(os.path.join(image_dir, filename))



run_image_analysis()

run_image_analysis(path='Media\Image\Cluster2.jpg', media='IMAGE')


# media = 'CAMERA', 'VIDEO' or 'IMAGE'
# for img_path in image_paths:
    # print(img_path)
    # run_image_analysis(path=img_path, media='IMAGE')
