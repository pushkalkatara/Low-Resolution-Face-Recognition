
sudo apt-get update -y
sudo apt-get install -y libsm6 libxext6 libxrender-dev ffmpeg build-essential libssl-dev libffi-dev python-dev python3-pip

pip3 install -r requirements-gpu.txt

sudo iptables -I INPUT -p tcp -s 0.0.0.0/0 --dport 5000 -j ACCEPT
sudo service netfilter-persistent save