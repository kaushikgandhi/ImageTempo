sudo apt-get install build-essential
git clone https://github.com/Itseez/opencv.git
sudo apt-get install cmake
cd opencv
mkdir release
cd release
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
make
sudo make install
