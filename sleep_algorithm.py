from __future__ import print_function
from time import sleep
from pymoduleconnector import ModuleConnector
from Adafruit_IO import *


class SleepDetector:
    def __init__(self, device_name):
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

        self.movement_slow = []
        self.activity_score = [100] * 6  # Initial movement data
        self.sleep_status = [1] * 18
        self.rescored_status = []
        self.count_4_min = 0
        self.count_10_min = 0
        self.count_15_min = 0
        self.occupied = False
        self.unoccupied_count = 4

        self.aio = Client('501a8c0fc893498699f4f5ba6b3b4e1c')
        self.aio.send('Sleep Report', 1)

    def detect_sleep(self):
        # Loop
        while(True):
            # Record movement data every 10s for 60s
            self.get_movement()
            
            # If occupied, compute sleep state
            if self.unoccupied_count < 4:
                # Compute sleep status for a single minute
                self.compute_sleep()
                # If sleep status has changed, send to panel
                self.send_sleep_status()

    def get_movement(self):
        # For one minute
        for i in range(0, 6):
            # Every 10s store movement (the 20s avg)
            rdata = None
            for j in range(0, 10):
                rdata = self.x4m200.read_message_respiration_sleep()
                print(rdata.movement_slow)
                # print("Frame: {} RPM: {} Distance: {} Movement Slow: {} Movement Fast: {}".format(rdata.frame_count, rdata.respiration_rate,rdata.distance, rdata.movement_slow,rdata.movement_fast))
                if rdata.movement_slow == 0 and self.occupied:
                    self.occupied = False
                    self.send_occupancy()
                elif rdata.movement_slow != 0 and not self.occupied:
                    self.occupied = True
                    self.send_occupancy()
                    self.unoccupied_count = 0


                #sleep(0.2)  # is this needed?
            self.movement_slow.append(rdata.movement_slow)
            print('Movement Slow {}'.format(self.movement_slow))
            if len(self.movement_slow) > 6:
                self.movement_slow.pop(0)

            self.aio.send('Sleep Data', rdata.movement_slow)

        if not self.occupied and self.unoccupied_count < 4:
            self.unoccupied_count += 1

    def compute_sleep(self):
        print(self.movement_slow)
        print(self.movement_slow[-1])
        if len(self.movement_slow) != 6:
            raise Exception(
                "Error. Must have 60s of\
                movement data to compute activity score.")

        # Add max movement in 1 minute to activity score
        self.activity_score.append(max(self.movement_slow))
        # self.movement_slow.clear()

        # Must have 7 minutes of data
        if len(self.activity_score) < 7:
            raise Exception(
                "Error. Must have 7 minutes of\
                movement data to compute sleep.")

        # Cole-Kripke Algorithm
        # status > 1 means awake
        status = 0.00001 * (
            404 * self.activity_score[0] +
            598 * self.activity_score[1] +
            326 * self.activity_score[2] +
            441 * self.activity_score[3] +
            1408 * self.activity_score[4] +
            508 * self.activity_score[5] +
            350 * self.activity_score[6])


        # 1: Awake
        # 0: Asleep
        if status > 1:
            self.sleep_status.append(1)
            self.rescored_status.append(1)
            if self.count_4_min < 4:
                self.count_4_min += 1
            if self.count_10_min < 10:
                self.count_10_min += 1
            if self.count_15_min < 15:
                self.count_15_min += 1
        else:
            self.rescore()
            self.sleep_status.append(0)
            self.count_4_min = 0
            if self.count_10_min < 10 or self.count_10_min > 13:
                self.count_10_min = 0
            else:
                self.count_10_min += 1

            if self.count_15_min < 15 or self.count_15_min > 19:
                self.count_15_min = 0

        self.activity_score.pop(0)
        print("Current Sleep status: {}".format(self.sleep_status[-1]))


    def rescore(self, status):
        if (self.count_4_min >= 4 or 
                self.count_10_min >= 10 or
                self.count_15_min >= 15): 
            self.rescored_status.append(1)
        else:
            self.rescored_status.append(0)



    def send_sleep_status(self):
        if(len(self.rescored_status) < 2):
            return
        # Send on state changes
        if(self.rescored_status[-1] != self.rescored_status[-2]):
            # Send http request to endpoint
            if self.rescored_status[-1] == 1:
                print("\nSleep State Change: Awake\n")
                self.aio.send('Sleep Report', 1)
            else:
                print("\nSleep State Change: Asleep\n")
                self.aio.send('Sleep Report', 0)

        if(len(self.rescored_status) > 1440):
            self.rescored_status.pop(0)
        if(len(self.sleep_status) > 1440):
            self.sleep_status.pop(0)

    def send_occupancy(self):
        if self.occupied:
            print("\nOccupancy Change: Occupied\n")
            self.aio.send('Occupancy Report', 1)
        else:
            print("\nOccupancy Change: Unoccupied\n")
            self.aio.send('Occupancy Report', 0)



def main():
    SD = SleepDetector('/dev/cu.usbmodem1421')#("/dev/ttyS0")
    SD.detect_sleep()


if __name__ == "__main__":
    main()
