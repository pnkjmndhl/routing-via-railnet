import sys
import os

filenames = [x.split('.')[0] for x in os.listdir('intermediate/') if '_' not in x]

os.system("python create_od.py")

for filename in filenames:
    os.system("python -W ignore snap.py "+filename)
    #os.system("python snap.py "+filename)

os.system("python append_scenario.py")
os.system("python rm_exceptions.py")
os.system("python gen_cm.py")

print("Completed.")
print("Make sure that all the scenario's are copied to Netdata folder")


