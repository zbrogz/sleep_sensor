pip2 install adafruit-io
unzip ModuleConnector-rpi-1.4.3.zip
cd python27-arm-linux-gnueabihf
python2 setup.py install
sed -i '/exit 0/i \
sudo python2 /home/pi/sleep_sensor/sleep_algorithm.py &' /etc/rc.local
echo Sleep Sensor Install Complete