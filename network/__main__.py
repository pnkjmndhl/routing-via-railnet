import os
import sys


try:
    argv = sys.argv[1]
except:
    argv = 'n'


if argv in ['-h', '-help']:
    print ("Usage: python network.py [-n|-u|-m|-s]")
    print ("-n: Generate/update new Node IDs")
    print ("-m: Auto-generate missing attributes")
    print ("-s: Generate Network file")
    exit(0)

if 'n' in argv:
    os.system("python network/generate_nodeids.py")
    os.system("python network/get_end_nodeids.py")
    os.system("python network/get_linkids.py")
    os.system("python network/overwrite_missing.py")
    os.system("python network/get_readable_attributes.py")
    os.system("python network/gen_networkfile.py")

elif 'm' in argv:
    os.system("python network/overwrite_missing.py")
    os.system("python network/get_readable_attributes.py")
    os.system("python network/gen_networkfile.py")
elif 's' in argv:
    os.system("python network/gen_networkfile.py")

else:
    print("Invalid Switch")
    exit(0)