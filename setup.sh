pip2 install adafruit-io
unzip ModuleConnector-rpi-1.4.3.zip
cd python27-arm-linux-gnueabihf
python2 setup.py install
grep -q -F 'sudo python2 /home/pi/sleep_sensor/sleep_algorithm.py &' /etc/rc.local || sudo sed -i "`wc -l < /etc/rc.local`i\\sudo python2 /home/pi/sleep_sensor/sleep_algorithm.py &\\" /etc/rc.local
echo Sleep Sensor Install Complete