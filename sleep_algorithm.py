from __future__ import print_function
from time import sleep
from pymoduleconnector import ModuleConnector
from Adafruit_IO import *

'''
Sleep/Occupancy States
Occupancy:      0 (unoccupied)      1 (Occupied)
Sleep:          0 (alseep)          1 (awake)      
'''
class SleepDetector:
    def __init__(self, device_name, test=False):
        print("Initializing")
        # Reset module
        self.mc = ModuleConnector(device_name)
        self.x4m200 = self.mc.get_x4m200()
        self.x4m200.module_reset()
        self.mc.close()
        sleep(3)

        # Assume an X4M300/X4M200 module and try to enter XEP mode
        self.mc = ModuleConnector(device_name)
        self.x4m200 = self.mc.get_x4m200()

        # Stop running application and set module in manual mode.
        try:
            # Make sure no profile is running
            self.x4m200.set_sensor_mode(0x01, 0)
        except RuntimeError:
            # Profile not running, OK
            pass

        # Load x4m200 respiration detection profile
        self.x4m200.load_profile(0x47fabeba)
        try:
            self.x4m200.set_sensor_mode(0x01, 0)  # RUN mode
        except RuntimeError:
            # Sensor already stopped, OK
            pass
        self.x4m200.set_output_control(0x610a3b00, 1)
        sleep(120) # Wait 2 minutes for init

        self.movement = None
        self.epoch = []
        self.activity = [100] * 6  # Initial movement data
        self.sleep = []
        self.rescored = []
        self.occupied = False
        self.aio = Client('da24bb7eb9fe4d4db98227da64e94191')
        

    def send_sleep(self):
        print("Current sleep state: {}".format(self.rescored[-1]))
        # Only send if sleep state has changed since last minute
        if ((len(self.rescored) > 1 and self.rescored[-1] != self.rescored[-2]) or
                len(self.rescored) == 1):
            if self.rescored[-1] == 1:
                print("\nSleep State Change: Awake\n")
                self.aio.send('Sleep', 1)
            else:
                print("\nSleep State Change: Asleep\n")
                self.aio.send('Sleep', 0)

        # Keep around 24 hours of sleep data
        # Change this to lower value to save memory
        if len(self.rescored) > 1440:
            self.rescored.pop(0)
        if len(self.sleep) > 1440:
            self.sleep.pop(0)


    def send_occupancy(self):
        if self.occupied:
            print("\nOccupancy Change: Occupied\n")
            self.aio.send('Occupancy', 1)
        else:
            print("\nOccupancy Change: Unoccupied\n")
            self.aio.send('Occupancy', 0)


    # Rescoring rules for reducing false positives of sleep detection
    def rescore(self):
        wake_4 = [1]*4
        wake_10 = [1]*10 
        wake_15 = [1]*15 

        # already awake, no rescore needed
        if self.sleep[-1] == 1:
            self.rescored.append(1)
            return
        # 4 min awake rescore next 1 min awake
        if (len(self.sleep) >= 5 and
                wake_4 == self.sleep[-5:-1]):
            self.rescored.append(1)
        # 10 min awake rescore next 3 min awake
        elif (len(self.sleep) >= 12 and
                wake_10 == self.sleep[-12:-2]):
            self.rescored.append(1)
        elif (len(self.sleep) >= 13 and
                wake_10 == self.sleep[-13:-3]):
            self.rescored.append(1)
        # 15 min awake rescore next 4 min awake
        elif (len(self.sleep) >= 19 and
                wake_15 == self.sleep[-19:-5]):
            self.rescored.append(1)
        # No change
        else:
            self.rescored.append(self.sleep[-1])

    
    def get_sleep(self):
        if len(self.activity) < 7:
            return

        # Cole-Kripke Algorithm
        # status >= 1 means awake
        status = 0.00001 * (
            404 * self.activity[-7] +
            598 * self.activity[-6] +
            326 * self.activity[-5] +
            441 * self.activity[-4] +
            1408 * self.activity[-3] +
            508 * self.activity[-2] +
            350 * self.activity[-1])
        status = 1 if status >= 1 else 0
        self.sleep.append(status)
        # Apply rescore rules
        self.rescore()
        # Send state on change
        self.send_sleep()
        self.activity.pop(0)


    def get_activity(self):
        self.activity.append(max(self.epoch))
        del self.epoch[:]


    def get_epoch(self):
        self.epoch.append(self.movement)
        print("Current epoch: {}".format(self.epoch[-1]))


    def get_movement(self):
        # Get movement slow (20s average of movement)
        rdata = self.x4m200.read_message_respiration_sleep()
        self.movement = rdata.movement_slow
        # Check occupancy, send on state changes
        if self.movement == 0 and self.occupied:
            self.occupied = False
            self.send_occupancy()
        elif self.movement != 0 and not self.occupied:
            self.occupied = True
            self.send_occupancy()


    def run(self):
        print("Running algorithm")
        # Every 60s
        for i in range(0, 6):
            # Every 10s
            for j in range(0,10):
                # get movement/occupancy every second
                self.get_movement()
            # record movement as epoch every 10 s
            self.get_epoch()
        # record activity as max epoch for 60s period
        # compute sleep from activity scores
        self.get_activity()
        self.get_sleep()


def main():
    SD = SleepDetector(device_name='/dev/ttyS0', test=False)#("/dev/cu.usbmodem1421")
    while(True):
        SD.run() # Begin algorithm


if __name__ == "__main__":
    main()
