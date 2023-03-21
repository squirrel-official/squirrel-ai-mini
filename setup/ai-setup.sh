# Ubuntu 20.04 server 64 bit
cd /usr/local/
sudo chmod -R 777 .

sudo apt update
sudo apt install python3-pip -y
sudo apt-get install libjpeg-dev zlib1g-dev  -y
sudo apt-get install libssl-dev -y
sudo apt-get install libgtk2.0-dev -y
sudo apt-get install pkg-config -y
sudo apt-get install ffmpeg libsm6 libxext6  -y
sudo apt-get update
sudo apt-get install -y cmake

pip3 install Pillow
pip3 install dlib
pip3 install face_recognition -v
pip3 install numpy --upgrade
pip3 install opencv-contrib-python -v
sudo apt-get install -y python3-opencv

pip3 install tflite-support
sudo apt install python3-h5py -y
pip3 install tensorflow-aarch64
sudo apt-get install libportaudio2
 sudo apt-get install libatlas-base-dev -y

sudo apt-get install v4l2loopback-dkms -y
sudo apt-get install avahi-dnsconfd -y
#Added for RaspberryPi
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install python3-tflite-runtime

sudo apt-get update
sudo apt-get upgrade



sudo chmod -R 777 .