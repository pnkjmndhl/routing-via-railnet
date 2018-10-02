import sys
import os

length = len(sys.argv)

for i in range(length-1):
    print("Working on "+sys.argv[i+1] + " ...")
    os.system("python run.py "+sys.argv[i+1])
    print("Completed.")
