
from Adafruit_IO import * #this imports everything from the Adafruit IO library
import time #this imports the library that will allow us to have a time delay

print("Start Test") #print to console to help us know that things have started

#This next line sets up our code to communicate with our specific dashboard
aio = Client('501a8c0fc893498699f4f5ba6b3b4e1c') #use the AIO KEY

#Send some intitial data to each of the feeds
aio.send('Sleep Data', 50) 
aio.send('Sleep Report', 1) 
aio.send('Occupancy Report', 0)

#send some progressive data to the feed to simulate getting data
for x in xrange(1,70): #repeat 7 times
	aio.send('Sleep Data', x) #send sleep data
	time.sleep(2) #delay each report by 1 second - Adafruit IO throttles feeds that report too often

#send some data to finish up
aio.send('Sleep Report', 0)
aio.send('Occupancy Report', 1)

print("All done") #print to console to show we're done