# Low Resolution Face Recognition

## Basic Instalation - UBUNTU

1) Clone this project:<br />
$ git clone https://github.com/pushkalkatara/Low-Resolution-Face-Recognition

2) Go to Face Recognition folder:<br />
$ cd Low-Resolution-Face-Recognition

3) Install the application:
    - If you have CPU:<br />
        $ chmod +x install-app-cpu.sh<br />
        $ ./install-app-cpu.sh

    - If you have GPU:<br />
        $ chmod +x install-app-gpu.sh<br />
        $ ./install-app-gpu.sh
		
4) Start the application:<br />
$ ./start-app.sh

5) Open your browser and access the Console:<br />
    http://<HOST_IP>:5000/ui

## Usage

1) /face/add: This operation adds a new human face to the Face Recognition API database. You can upload videos or images that contain only one person.

2) /face/classify: This opertaion to execute a face recognition. You can upload images that contains only one person.

3) /face/train: This operation trains the model to recognize the new faces added by the "/face/add" operation.

4) /face/restart: This operation reloads the Face Recognition API model if you experience any problems.


## Inspiration

I use the ![Facenet](https://github.com/davidsandberg/facenet) implementation in this code.
I use the ![SRGAN](https://github.com/tadax/srgan) implementation in this code.
I use the ![face_recognition_api](https://github.com/waslleysouza/face_recognition_api) reference in this code.

## License

This project is ![MIT License](LICENSE.md)
