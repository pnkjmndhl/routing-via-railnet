# run and backup the run
import os
import sys
import datetime

# Network Parameter File: network.prm
# Link Data File: network.dat
# Transfer Data File: network.exc
#
# Commodity File: base.dat
# Network Paremeter File: network.prm
# Positive Number: 365
#
# Network Parameter File: network.prm
# Commodity File: base.xcq
# Default Cost file: cost.dat
# Transfer Exception File: transfer.exc
# Link Exception File: link.exc
# Link Volume File: volume.lvl


network_prm = sys.argv[1]
link_dat = sys.argv[2]
transfer_xfr = sys.argv[3]
commodity_dat = sys.argv[4]
positive_number = sys.argv[5]
cost_dat = sys.argv[6]
transfer_exc = sys.argv[7]
link_exc = sys.argv[8]
link_volume_lvl = sys.argv[9]
netbld = sys.argv[10]
commodty = sys.argv[11]
railnet = sys.argv[12]

now = datetime.datetime.now()
folder_name = now.strftime("%Y-%m-%d_%H%M%S") + "_" + commodity_dat.split('.')[0]

readme_name = "Readme.txt"
readme_path = "Backups\\" + folder_name + "\\" + readme_name

arguments_full = ['Python File Name', 'Network Parameter File', 'Link Data File', 'Transfer Exception Data File',
                  'Commodity File', 'Positive Number', 'Default Cost file', 'Transfer Exception File',
                  'Link Exception File', 'Link Volume File', "NETBLD", "COMMODTY", "RAILNET"]

os.system("mkdir Backups\\" + folder_name)
for args in sys.argv[1:]:
    os.system("copy " + args + ' Backups\\' + folder_name)

os.chdir('Backups/' + folder_name)

os.system("ECHO ******************************************************** > " + readme_name)
os.system("ECHO. >> " + readme_name)
os.system("ECHO Parameters Used: >> " + readme_name)
for index in range(len(sys.argv[0:])):
    os.system("ECHO " + arguments_full[index] + ":" + sys.argv[index] + " >> " + readme_name)
os.system("ECHO ******************************************************** >> " + readme_name)
os.system("ECHO. >> " + readme_name)
os.system("ECHO. >> " + readme_name)

os.system(netbld + " " + network_prm + " " + link_dat + " " + transfer_xfr + " >> " + readme_name)
os.system(commodty + " " + commodity_dat + " " + network_prm + " " + positive_number + " >> " + readme_name)
os.system(railnet + " " + network_prm + " " + commodity_dat.split('.')[
    0] + '.xcq' + " " + cost_dat + " " + transfer_exc + " " + link_exc + " " + link_volume_lvl + "  >> " + readme_name)
