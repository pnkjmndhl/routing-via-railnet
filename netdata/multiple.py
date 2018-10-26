import sys
import os
import thread
import time
length = len(sys.argv)

for i in range(length-1):
    print(sys.argv[i+1] + " added to thread: " + str(thread.start_new_thread(os.system, ( "python run.py "+sys.argv[i+1],))))
    time.sleep(10)

print("Running in background... Please wait for results...")
