import sys
import os
import thread
import time
import psutil

# default CPU usage
default_max_cpu_usage = 70

# Default values:
network_prm_ = ['network.prm']
link_dat_ = ['network.dat']
transfer_xfr_ = ['network.xfr']
commodity_dat_ = ['base.dat']
positive_number_ = ['365']
cost_dat_ = ['cost.dat']
transfer_exc_ = ['transfer.exc']
link_exc_ = ['link.exc']
link_volume_lvl_ = ['volume.lvl']
netbld_ = ["NETBLD.exe"]
commodty_ = ["COMMODTY.exe"]
railnet_ = ["RAILNET.exe"]


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
                                                while (psutil.cpu_percent() > default_max_cpu_usage):
                                                    time.sleep(10)
                                                    print(
                                                        "Maximum CPU usage reached... waiting for other processes to complete")
                                                command_string = "python run.py " + network_prm + " " + link_dat + " " + transfer_xfr + " " + commodity_dat + " " + positive_number + " " + cost_dat + " " + transfer_exc + " " + link_exc + " " + link_volume_lvl + " " + netbld + " " + commodty + " " + railnet
                                                print(command_string + " added to thread: " + str(
                                                    thread.start_new_thread(os.system, (command_string,))))
                                                time.sleep(1)
print("Running in background... Please wait for results...")
