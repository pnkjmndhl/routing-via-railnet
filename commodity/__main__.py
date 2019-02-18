import sys
import os
from rail import *

os.system("python commodity/create_od.py")
print("Create OD completed")
print("*************************************")

filenames = [x.split('.')[0] for x in os.listdir(commodity_intermediate_path) if '_' not in x]
print("commodity files found: {0}".format(filenames))

for filename in filenames:
    os.system("python -W ignore commodity/snap.py "+filename)
    #os.system("python snap.py "+filename)
print("Snapping Completed")
print("*************************************")

os.system("python commodity/append_scenario.py")
print("Appending scenarion completed")
print("*************************************")
os.system("python commodity/rm_exceptions.py")
print("Removing exceptions completed")
print("*************************************")
os.system("python commodity/gen_cm.py")
print("Generating Commodity file completed")
print("*************************************")
print("Completed.")
print("Make sure that all the scenario's are copied to Netdata folder")


