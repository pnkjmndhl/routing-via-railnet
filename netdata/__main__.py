import sys
import os
import thread
import time
import psutil
import re
import datetime

# default CPU usage
default_max_cpu_usage = 70

now = datetime.datetime.now()
folder_name = now.strftime("%Y%m%d%H%M%S")

# Default values get from folder
file_names = os.listdir("./netdata/")
all_filenames = " ".join(file_names)
network_prm_ = re.findall("(?i) ([A-z0-9]*\.prm)",all_filenames)
link_dat_ = re.findall("(?i) (net[A-z0-9]*\.dat)",all_filenames)
transfer_xfr_ = re.findall("(?i) ([A-z0-9]*\.xfr)",all_filenames)
cost_dat_ = re.findall("(?i) (cos[A-z0-9]*\.dat)",all_filenames)
transfer_exc_ = re.findall("(?i) (tra[A-z0-9]*\.exc)",all_filenames)
link_exc_ = re.findall("(?i) (lin[A-z0-9]*\.exc)",all_filenames)
link_volume_lvl_ = re.findall("(?i)([A-z0-9]*\.lvl)",all_filenames)
netbld_ = re.findall("(?i) (net[A-z0-9]*\.exe)",all_filenames)
commodty_ = re.findall("(?i) (com[A-z0-9]*\.exe)",all_filenames)
railnet_ = re.findall("(?i) (rai[A-z0-9]*\.exe)",all_filenames)
positive_number_ = ['365']
commodity_dat_ = [x for x in re.findall("(?i) ([A-z0-9]*\.dat)",all_filenames) if x not in link_dat_+cost_dat_]
print "Commodity files: {0}:".format(commodity_dat_)
folder_ = [folder_name]


def assign_value(name, list):
    global network_prm_
    global link_dat_
    global transfer_xfr_
    global commodity_dat_
    global positive_number_
    global cost_dat_
    global transfer_exc_
    global link_exc_
    global link_volume_lvl_
    global netbld_
    global commodty_
    global railnet_
    if name == 'network_prm_':
        network_prm_ = list
    elif name == 'link_dat_':
        link_dat_ = list
    elif name == 'transfer_xfr_':
        transfer_xfr_ = list
    elif name == 'commodity_dat_':
        commodity_dat_ = list
    elif name == 'cost_dat_':
        cost_dat_ = list
    elif name == 'transfer_exc_':
        transfer_exc_ = list
    elif name == 'link_exc_':
        link_exc_ = list
    elif name == 'link_volume_lvl_':
        link_volume_lvl_ = list
    elif name == 'netbld_':
        netbld_ = list
    elif name == 'commodty_':
        commodty_ = list
    elif name == 'railnet_':
        railnet_ = list
    elif name == 'folder_':
        folder_ = list
    else:
        print("Parameter {0} not found in default values".format(name))
        exit(0)


# arguments to list:
def argument_to_list(argv):
    parameter_name = argv.split('~')[0]
    parameter_list = argv.split('~')[1].split('+')
    assign_value(parameter_name, parameter_list)
    print("{0} added as arguments".format(parameter_name))


try:
    sys.argv
except:
    pring("No arguments provided. Running with default parameters")
    command_string = "python run.py " + network_prm_[0] + " " + link_dat_[0] + " " + transfer_xfr_[0] + " " + \
                     commodity_dat_[0] + " " + positive_number_[0] + " " + cost_dat_[0] + " " + transfer_exc_[0] + " " + \
                     link_exc_[0] + " " + link_volume_lvl_[0] + " " + netbld_[0] + " " + commodty_[0] + " " + railnet_[
                         0]
    print(command_string + " added to thread: " + str(thread.start_new_thread(os.system, (command_string,))))
    exit(0)

for arguments in sys.argv[1:]:
    argument_to_list(arguments)

for network_prm in network_prm_:
    for link_dat in link_dat_:
        for transfer_xfr in transfer_xfr_:
            for commodity_dat in commodity_dat_:
                for positive_number in positive_number_:
                    for cost_dat in cost_dat_:
                        for transfer_exc in transfer_exc_:
                            for link_exc in link_exc_:
                                for link_volume_lvl in link_volume_lvl_:
                                    for netbld in netbld_:
                                        for commodty in commodty_:
                                            for railnet in railnet_:
                                                for folder in folder_:
                                                    while (psutil.cpu_percent() > default_max_cpu_usage):
                                                        time.sleep(10)
                                                        print(
                                                            "Maximum CPU usage reached... waiting for other processes to complete")
                                                    command_string = "python netdata/run.py " + network_prm + " " + link_dat + " " + transfer_xfr + " " + commodity_dat + " " + positive_number + " " + cost_dat + " " + transfer_exc + " " + link_exc + " " + link_volume_lvl + " " + netbld + " " + commodty + " " + railnet + " " + folder
                                                    print(command_string + " added to thread: " + str(
                                                        thread.start_new_thread(os.system, (command_string,))))
                                                    time.sleep(1)
print("Running in background... Please wait for results...")
