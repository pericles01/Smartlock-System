# Usefull Links:
# https://kivy.org/doc/stable/gettingstarted/installation.html#kivy-source-install
# https://kivy.org/doc/stable/installation/installation-rpi.html
# https://kivymd.readthedocs.io/en/1.1.1/getting-started/

# update os packages & install python, pip
cd ..
sudo apt update
sudo apt install python3 python3-pip

# install required dependencies for kivy 
sudo apt-get -y install build-essential git make autoconf automake libtool \
      pkg-config cmake ninja-build libasound2-dev libpulse-dev libaudio-dev \
      libjack-dev libsndio-dev libsamplerate0-dev libx11-dev libxext-dev \
      libxrandr-dev libxcursor-dev libxfixes-dev libxi-dev libxss-dev libwayland-dev \
      libxkbcommon-dev libdrm-dev libgbm-dev libgl1-mesa-dev libgles2-mesa-dev \
      libegl1-mesa-dev libdbus-1-dev libibus-1.0-dev libudev-dev fcitx-libs-dev libcamera-apps

sudo apt-get install xorg wget libxrender-dev lsb-release libraspberrypi-dev raspberrypi-kernel-headers
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt install libpango1.0-dev xclip xsel
sudo apt install libavcodec-dev libavdevice-dev libavfilter-dev libavformat-dev libavutil-dev libswscale-dev libswresample-dev libpostproc-dev
sudo apt-get install -y mtdev-tools
sudo apt-get install graphicsmagick  libgraphicsmagick1-dev libatlas-base-dev libavcodec-dev libavformat-dev libboost-all-dev  libgtk2.0-dev  libjpeg-d \
      liblapack-dev libswscale-dev  pkg-config gfortran
sudo apt install -y python3-picamera2

sudo apt install libxcb-cursor0

sudo apt update
sudo apt upgrade

# create & activate a virtual environment for the dependencies
python3 -m venv Vapp --system-site-packages
source Vapp/bin/activate

# The script will download and build the SDL dependencies from source. 
# It will also install the dependencies into a directory named kivy-dependencies. 
#This directory will be used by Kivy to build and install Kivy from source with SDL support.
mkdir kivy-deps-build && cd kivy-deps-build
curl -O https://raw.githubusercontent.com/kivy/kivy/master/tools/build_linux_dependencies.sh
bash build_linux_dependencies.sh

# Kivy will need to know where the SDL dependencies
export KIVY_DEPS_ROOT=$(pwd)/kivy-dependencies
echo $KIVY_DEPS_ROOT

# Install the stable version of Kivy & KivyMD
cd ..
pip3 install "kivy[base]" kivy_examples --no-binary kivy
pip3 install kivymd

# Install other project's libraries
pip3 install pyserial pandas
pip3 install qrcode
pip3 install opencv-python dlib face_recognition
pip3 install scikit-learn
pip3 install gpiozero

# enable hardware acceleration
sudo adduser "$USER" render
