import numpy as np
import cv2
import os
import io
import json
from datetime import datetime
from PIL import Image
import multiprocessing
import classifier
import align.align_dataset_mtcnn
import ffmpeg
import oci
import oci_utils
import utils
import face


# load settings
datastore = utils.load_json_file("deployment.json")


IMAGE_UPLOAD_DIR = datastore["IMAGE_UPLOAD_DIR"]
IMAGE_ORIGINAL_DIR = datastore["IMAGE_ORIGINAL_DIR"]
IMAGE_PREPARED_DIR = datastore["IMAGE_PREPARED_DIR"]
MODEL_PATH = datastore["MODEL_PATH"]
CLASSIFIER_PATH = datastore["CLASSIFIER_PATH"]
OCI_CONFIG_PATH = datastore["OCI_CONFIG_PATH"]
OCI_STORAGE_BUCKET_NAME = datastore["OCI_STORAGE_BUCKET_NAME"]
OCI_STORAGE_SYNC = datastore["OCI_STORAGE_SYNC"]
CLASSIFY_IMAGE_WIDTH = datastore["CLASSIFY_IMAGE_WIDTH"]
ADD_FRAMES_PER_VIDEO = datastore["ADD_FRAMES_PER_VIDEO"]


def classify(file):
    print("Method", "facerec_service.classify")
    image = Image.open(io.BytesIO(file.read()))
    image = image.convert('RGB')
    utils.resize_image(image, CLASSIFY_IMAGE_WIDTH)
    image.save(os.path.join(IMAGE_UPLOAD_DIR, "classify_" + file.filename.lower()))
    
    faces = face_recognition.identify(np.array(image))

    if faces is not None:
        if faces[0]:
            print(faces[0].name)
            return json.dumps({'result': 'success', 'name': faces[0].name})
			
    return json.dumps({'result': 'success', 'message': 'error'})


def train():
    print("Method", "facerec_service.train")
    align.align_dataset_mtcnn.main(align.align_dataset_mtcnn.parse_arguments([IMAGE_ORIGINAL_DIR, IMAGE_PREPARED_DIR]))
    classifier.main(classifier.parse_arguments(['TRAIN', IMAGE_PREPARED_DIR, MODEL_PATH, CLASSIFIER_PATH]))
    

def restart():
    global face_recognition
    face_recognition = face.Recognition()


def add(file, name, rotate):
    print("Method", "facerec_service.add")

    file_type = utils.get_content_type(file)[0]
    file_extension = utils.get_content_type(file)[1]

    if file_type not in ['image', 'video']:
        return json.dumps({'result': 'error', 'message': 'Invalid File!'})

    datetime_format = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = "add_{}_{}_1.{}".format(name, datetime_format, file_extension).lower()
    file.save(os.path.join(IMAGE_UPLOAD_DIR, filename))
    file = os.path.join(IMAGE_UPLOAD_DIR, filename)
    utils.create_directory(os.path.join(IMAGE_ORIGINAL_DIR, name))

    probe = ffmpeg.probe(file)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    rotate = video_stream['tags']['rotate'] if 'tags' in video_stream and 'rotate' in video_stream['tags'] else rotate
    
    filename_list = []
    if file_type == 'image':
        image = cv2.imread(file)

        if rotate is not None:
            image = utils.rotate_cv2_image(image, rotate)

        filename = name + "/" + "{}_{}.{}".format(name, datetime_format, file_extension).lower()
        filename_list.append(filename)
        utils.save_cv2_image(IMAGE_ORIGINAL_DIR, filename, image)
    
    else:
        cap = cv2.VideoCapture(file)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_count = ADD_FRAMES_PER_VIDEO if frame_count > ADD_FRAMES_PER_VIDEO else frame_count    
        frame_no = 0
        count = 1
        
        while frame_no < frame_count:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            if ret:
                if rotate is not None:
                    frame = utils.rotate_cv2_image(frame, rotate)
                    
                filename = name + "/" + "{}_{}_{}.jpg".format(name, datetime_format, count).lower()
                filename_list.append(filename)
                utils.save_cv2_image(IMAGE_ORIGINAL_DIR, filename, frame)
                count += 1
            
            frame_no += 1
    
    if OCI_STORAGE_SYNC:
        pool = multiprocessing.pool.ThreadPool(processes=3)
        pool.apply_async(oci_utils.upload_to_object_storage, args=[config, IMAGE_ORIGINAL_DIR, OCI_STORAGE_BUCKET_NAME, filename_list])
        pool.close()

    return json.dumps({'result': 'success', 'message': 'File uploaded!'})


print("facerec_service loaded!")
utils.create_directories([IMAGE_UPLOAD_DIR, IMAGE_ORIGINAL_DIR, IMAGE_PREPARED_DIR])
config = oci.config.from_file(OCI_CONFIG_PATH, "DEFAULT")

if OCI_STORAGE_SYNC:
    oci_utils.syncronize_with_object_storage(config, IMAGE_ORIGINAL_DIR, OCI_STORAGE_BUCKET_NAME)
	
face_recognition = face.Recognition()
#train()