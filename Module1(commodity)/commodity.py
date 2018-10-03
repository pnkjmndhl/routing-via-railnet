import sys
import os


os.system("python create_od.py base")

os.system("python snap.py base update")

os.system("python add_scenario.py")

os.system("python rm_exceptions.py")

os.system("python gen_cm.py")




