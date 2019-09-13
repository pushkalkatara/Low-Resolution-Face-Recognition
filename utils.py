import cv2
import os
import json
from PIL import Image


def get_content_type(file):
    return file.content_type.split("/")


def create_directories(directory_list):
    for path in directory_list:
        create_directory(path)


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print("Directory created: {!r}".format(path))


def resize_image(image, width):
    if image.size[1] >= width:
        wpercent = (width / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        image = image.resize((width, hsize), Image.ANTIALIAS)


def get_rotate_code(rotate):
    rotate_code = cv2.ROTATE_90_CLOCKWISE
    if rotate == 180:
        rotate_code = cv2.ROTATE_180
    elif rotate == 270:
        rotate_code = cv2.ROTATE_90_COUNTERCLOCKWISE
    return rotate_code


def load_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def rotate_cv2_image(cv2_image, rotate):
    if rotate is not None:
        return cv2.rotate(cv2_image, rotateCode=get_rotate_code(int(rotate)))


def save_cv2_image(directory, image_name, cv2_image):
    image_path = os.path.join(directory, image_name)
    cv2.imwrite(image_path, cv2_image)
    print("File created: {!r}".format(image_path))