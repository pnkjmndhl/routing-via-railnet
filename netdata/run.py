# run and backup the run

import os
import sys
import datetime

commodity_name = sys.argv[1]

now = datetime.datetime.now()
folder_name = now.strftime("%Y-%m-%d_%H%M") + commodity_name


if len(sys.argv) == 3:
    description = sys.argv[2]
else:
    description = ""

readme_name = "Readme_"+commodity_name+".txt"


os.system("ECHO "+description+ " > "+readme_name)

os.system("NETBLD network network network  >> "+readme_name)
os.system("COMMODTY "+commodity_name+" network 365  >> "+readme_name)
os.system("RAILNET network "+commodity_name+" cost transfer.exc link.exc volume.lvl  >> "+readme_name)
#os.system("RAILNET network "+commodity_name+" cost transfer.exc link.exc >> "+readme_name)


export_name_list = os.listdir('.')
export_name_list = [x for x in export_name_list if ((commodity_name in x) or ((commodity_name.upper() in x))) ]
#export_name_list = list(set(i.lower() for i in export_name_list))

#keep both copies extensions
keep_both_copies_extension_list = ['LMF', 'dat']
os.system("mkdir Backups\\"+folder_name + " >> "+readme_name)


for extension in keep_both_copies_extension_list:
    export_name_list.remove(commodity_name + "." + extension)
    os.system("copy " + commodity_name + '.' + extension + ' Backups\\' + folder_name + " >> "+readme_name)


# also copy remaining files :)
for file_names in export_name_list:
    os.system("move "+file_names+ " Backups\\"+folder_name + " >> "+readme_name)


# copying parameter files
parameter_files = ['network.dat', 'cost.dat', 'link.exc', 'network.PRM', 'network.xfr', 'transfer.exc', 'volume.lvl']
for file_names in parameter_files:
    os.system("copy "+file_names+ " Backups\\"+folder_name + " >> "+readme_name)


#finally copy the read_me file
os.system("move Readme_"+commodity_name+ ".txt Backups\\"+folder_name)