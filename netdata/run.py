# run and backup the run
import os
import sys
import datetime
import time

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

# sleeping for a second creates different values for argument 13 and now.strftime, thus creating writing the date/time in each file
time.sleep(1)

now = datetime.datetime.now()

# Default values:
default_values = ['network.prm', 'network.dat', 'network.xfr', 'base.dat', '365', 'cost.dat', 'transfer.exc',
                  'link.exc', 'volume.lvl', "NETBLD.exe", "COMMODTY.exe", "RAILNET.exe", now.strftime("%Y%m%d%H%M%S")]

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
multiple_folder_name = sys.argv[13]

non_default_values = [x.split(".")[0] for x in sys.argv[1:] if x not in default_values]

non_default_values = [x for x in non_default_values if commodity_dat.split(".")[0] != x]

non_default_values_string = "_".join(str(x) for x in non_default_values)

print ("Output LMF Name: " + commodity_dat.split('.')[0] + "_" + non_default_values_string + ".LMF")

# calculation of


folder_name = multiple_folder_name + "\\" + now.strftime("%Y-%m-%d_%H%M%S") + "_" + commodity_dat.split('.')[0]

readme_name = "Readme.txt"
readme_path = "Backups\\" + folder_name + "\\" + readme_name

arguments_full = ['Python File Name', 'Network Parameter File', 'Link Data File', 'Transfer Exception Data File',
                  'Commodity File', 'Positive Number', 'Default Cost file', 'Transfer Exception File',
                  'Link Exception File', 'Link Volume File', "NETBLD", "COMMODTY", "RAILNET", "Folder Name"]

os.system("mkdir Backups\\" + folder_name)
for args in sys.argv[1:]:
    os.system("copy " + args + ' Backups\\' + folder_name + "> NUL")

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

# copy it to LMF folder and rename
# make directory if not present
if not os.path.exists("../../../LMF/" + multiple_folder_name):
    os.makedirs("../../../LMF/" + multiple_folder_name)

if not os.path.exists("../../../ADF/" + multiple_folder_name):
    os.makedirs("../../../ADF/" + multiple_folder_name)


os.system("copy " + commodity_dat.split('.')[0] + ".LMF " + "..\\..\\..\\LMF\\" + multiple_folder_name + "\\" +
          commodity_dat.split('.')[
              0] + "_" + non_default_values_string + ".LMF")
os.system("copy " + commodity_dat.split('.')[0] + ".ADF " + "..\\..\\..\\ADF\\" + multiple_folder_name + "\\" +
          commodity_dat.split('.')[
              0] + "_" + non_default_values_string + ".ADF")