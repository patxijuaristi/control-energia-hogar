import sys
from shelly_info import Shelly_info
from datetime import datetime
from time import sleep

s = Shelly_info()
print("Start")
s.start_periodic_upload()
print("Started")
while True:
    print(datetime.now())
    sys.stdout.flush()
    sleep(60*5)