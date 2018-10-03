import sys
import os

if sys.argv[1] in ['-h', '-help']:
    print("Usage: python commodity.py [-n|-u|-s]")

os.system("python create_od.py base")

if 'n' in sys.argv[1]:
    os.system("python snap.py base new")
elif 'u' in sys.argv[1]:
    os.system("python snap.py base update")
else:
    print("No switch for snap.py provided. Updating...")
    os.system("python snap.py base update")

if 's' in sys.argv[1]:
    os.system("python add_scenario.py")

os.system("python rm_exceptions.py")

os.system("python gen_cm.py")




