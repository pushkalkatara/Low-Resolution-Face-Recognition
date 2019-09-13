"""
This module serves as the API provider for face processing.
"""

import json
import multiprocessing
import requests
import facerec_service


processes = 3


def train():
    print("Method", "train")
    pool = multiprocessing.pool.ThreadPool(processes=processes)
    pool.apply_async(facerec_service.train, callback=train_callback)
    pool.close()
    return json.dumps({'result': 'success', 'message': 'Model will be trained!'})
	

def train_callback(result):
    requests.post('http://localhost:5000/face/restart')


def restart():
    print("Method", "restart")
    facerec_service.restart()
    return json.dumps({'result': 'success', 'message': 'Model restarted!'})
	

def classify(file):
    print("Method", "classify")
    return facerec_service.classify(file)


def add(file, personName, rotate=None):
    print("Method", "add")
    return facerec_service.add(file, personName, rotate)