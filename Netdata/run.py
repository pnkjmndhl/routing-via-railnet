# run and backup the run

import os
import sys
import datetime

commodity_name = sys.argv[1]
commodity_name_upper = commodity_name.upper()

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

export_extensions = ['txt','dat','PRM','exc','xfr','XNQ', 'RPT', 'OUT']
delete_extensions = ['txt', 'NMF', 'XCQ', 'OUT', 'RPT']

export_list = os.listdir('.')
export_list = [x for x in export_list if ((commodity_name in x) or ((commodity_name_upper in x))) ]


os.system("mkdir Backups\\"+folder_name)

for file_names in export_list:
    os.system("copy "+file_names+ " Backups\\"+folder_name)


for extension in export_extensions:
    os.system("copy *."+extension+ " Backups\\"+folder_name)
    

for extension in delete_extensions:
    os.system("del *."+extension)