import urllib.request
import os
from PIL import Image

image_url = "https://raw.githubusercontent.com/AprilRobotics/apriltag-imgs/master/tag36h11/tag36_11_{0}.png"


def resize_image(input_image_path,
                 output_image_path,
                 size):
    original_image = Image.open(input_image_path)
    resized_image = original_image.resize(size, resample=0)
    resized_image.save(output_image_path)


if __name__ == '__main__':
    start_ = int(input("Initial ArucoTag ID: "))
    end_ = int(input("Final ArucoTag ID: "))
    try:
        os.mkdir("ArucoTags")
    except FileExistsError:
        pass
    for i in range(start_, end_+1):
        imgUrl = image_url.format("0" * (5 - len(str(i))) + str(i))
        urllib.request.urlretrieve(imgUrl, "ArucoTags/tag_now.png")
        resize_image(input_image_path='ArucoTags/tag_now.png',
                     output_image_path='ArucoTags/tag36_11_{0}.png'.format("0" * (5 - len(str(i))) + str(i)),
                     size=(640, 640))
        print("Done {0}%".format(int((i+1 - start_) / (end_-start_+1) * 100)))
    os.remove('ArucoTags/tag_now.png')
