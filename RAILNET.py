from rail.py import *
import os

os.system("python network")

os.system("python transfers")

os.system("python cost")
os.system("python exceptions")

os.system("python commodity")

os.system("xcopy output\*.* netdata\ /Y")

os.system("python netdata")

os.system("python plot")

os.system("pyhon web")