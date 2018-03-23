# sleep_sensor
Algorithm for detecting sleep and occupancy using the XeThru X4M200 and host device.

## Setup
The X4M200 can interface with pretty much any host computer/MCU with UART/USRT/USB communication. This specific guide provides instructions for running the device on a Raspberry Pi Zero W or a Mac.

### Mac
This installation was done on macOS High Sierra (10.13.2)
#### Hardware
Connect the XeThru to the Mac over usb using a micro usb male to usb male cord.
#### Software

1. Install Python 2
  - This is easiest using Homebrew: https://brew.sh/
  - `sudo brew install python2`
  - Otherwise macOS comes built with a slightly older version of python 2 that should work still.
2. Install XeThru ModuleConnector

... To be continued


### Raspberry Pi
1. Write raspbian OS to a micro SD card: https://www.raspberrypi.org/documentation/installation/installing-images/README.md
  - 2017-11-29-raspbian-stretch at the time of this writing
2. Pre-configure the network settings on the sd card
  - Navigate into the SD card boot folder: `cd /Volumes/<name of sd card>/boot`
  - Create an empty file called 'ssh' in /boot: `touch ssh`
  - Create and edit file called 'wpa_supplicant.conf': `vim wpa_supplicant.conf`
  - Write the following to the file, replacing the Wifi ssid and password:
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="your_real_wifi_ssid"
    scan_ssid=1
    psk="your_real_password"
    key_mgmt=WPA-PSK
}
```
3. Place the SD card into the raspberry pi and power it up
4. Wait a few minutes for the OS to initialize for the first time
5. SSH into the pi while connected to the same WiFi: `ssh pi@raspberrypi.local`
  - The default password is 'raspberry'
6. Configure rpi options
  - `raspi-config`
  - 'Change User Password' for security
  - 'Interfacing Options'
  - 'Serial'
  - Select 'No' for login shell
  - Select 'Yes' to enable serial port
  ...
8. Install XeThru ModuleConnector
...
9. Install AdafruitIO package for Python 2: `sudo pip2 install adafruit-io`
10. Download the sleep algorithm: `git clone https://github.com/zbrogz/sleep_sensor.git`
11. Configure the algorithm to run at boot:
...
12. Connect the UART pins of the Raspberry pi to 
