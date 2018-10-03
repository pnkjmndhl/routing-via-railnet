import os
import sys


if len(sys.argv[1])==0:
    print("No arguments provided.")
    print("Generating Network file in output..")
    os.system("python gen_networkfile.py")

if sys.argv[1] in ['-h', '-help']:
    print ("Usage: python network.py [-n|-u|-m|-s]")
    print ("-n: Generate new Node IDs")
    print ("-u: Update Node IDs")
    print ("-n: Auto-generate missing attributes")
    print ("-s: Generate Network file")
    exit(0)

if 'n' in sys.argv[1]:
    os.system("python generate_nodeids.py new")
    os.system("python get_end_nodeids.py")
    os.system("python get_linkids.py")
    os.system("python overwrite_missing.py")
    os.system("python get_readable_attributes.py")
    os.system("python gen_networkfile.py")
elif 'u' in sys.argv[1]:
    os.system("python generate_nodeids.py update")
    os.system("python get_end_nodeids.py")
    os.system("python get_linkids.py")
    os.system("python overwrite_missing.py")
    os.system("python get_readable_attributes.py")
    os.system("python gen_networkfile.py")
elif 'm' in sys.argv[1]:
    os.system("python overwrite_missing.py")
    os.system("python get_readable_attributes.py")
    os.system("python gen_networkfile.py")
elif 's' in sys.argv[1]:
    os.system("python gen_networkfile.py")
else:
    print("Invalid Switch")
    exit(0)