import re
import pandas


network_DF = pandas.read_csv('input/network.csv')
link_DF = network_DF.set_index('ID')

commodity_name = 'S3'
out_file = 'input/'+commodity_name + '.OUT'


def getindices(vookup_pattern, list):
    indexes = []
    for i in range(len(list)):
        if (re.search(vookup_pattern, list[i]) != None):
            indexes.append(i)
    return indexes

def get_start_pattern(chomp, re_pattern, rr):
    indexes_all = []
    index_rr = []
    for i in range(len(chomp)):
        if (re.search(re_pattern, chomp[i]) != None):
            indexes_all.append(i)
    for j in indexes_all:
        rr_re = int(re.search(re_pattern, chomp[j]).group(2))
        if rr_re == rr:
            index_rr.append(j)
    return index_rr

def get_rrs_in_chomped():
    rrs = []
    for lines in range(len(chomped)):
        try:
            rr = re.search(volumes_re, chomped[lines]).group(2)
            rrs.append(int(rr))
        except:
            pass
    rrs = list(set(rrs))
    return rrs

def get_end_index(chomp, start_index):
    for i in range(start_index+1,len(chomp)):
        if (re.search(cm_re, chomp[i]) == None):
            break
    return i

with open(out_file) as f:
    content_all = f.readlines()



index_of_start = content_all.index(' **** Link Volumes ****\n')
content_all = content_all[index_of_start+2:len(content_all)+1]

#do calculation
indexes_results = [1 if ' ** Results for link' in x else 0 for x in content_all]
indices_results = [i for i, x in enumerate(indexes_results) if x == 1]


link_DF['actualruntime'] = ""
link_DF['delay'] = ""

for indexes in range(len(indices_results)-1):

    chomped = content_all[indices_results[indexes]:indices_results[indexes+1]]
    line1_re = "Results for link\s*(\d+)  Type: \s*(\d+)"
    link_ID = int(re.search(line1_re, chomped[0]).group(1))
    print link_ID
    link_type = re.search(line1_re, chomped[0]).group(2)
    line2_re = "Ideal run time\s*(\d+\.\d+) hrs.  Actual run time \s*(\d+\.\d+) hrs.  Delay \s*(\d+\.\d+) hrs."
    if(re.search("\s*Total trains:", chomped[1]) != None):
        print("exited")
        continue
    print link_type
    if link_type == '3':
        try:
            ideal_run_time = re.search(line2_re, chomped[2]).group(1)
            actual_run_time = re.search(line2_re, chomped[2]).group(2)
            delay = re.search(line2_re, chomped[2]).group(3)
        except:
            continue
    else:
        try:
            ideal_run_time = re.search(line2_re, chomped[1]).group(1)
            actual_run_time = re.search(line2_re, chomped[1]).group(2)
            delay = re.search(line2_re, chomped[1]).group(3)
        except:
            continue
    railroads = get_rrs_in_chomped()
    volumes_re = "\s*Volumes for arc\s*(\d+) \s*Carrier:\s*(\d+)\s*Dir:\s*(\d+)"
    cm_re = "\s*CM:(\d+)\s*Gross Tons:\s*(\d+\.\d+)\s*Net Tons:\s*(\d+\.\d)\s*[A-Za-z\d:. ]*\\n"
    link_DF.loc[link_ID,'actualruntime'] = actual_run_time
    link_DF.loc[link_ID,'delay'] = delay
    print(link_ID)
    for rr in railroads:
        start_indexes = get_start_pattern(chomped, volumes_re, rr )
        start_end_dict = {x:get_end_index(chomped, x) for x in start_indexes }
        gross_tons = 0
        net_tons = 0
        for key, value in start_end_dict.iteritems():
            for j in range(key+1,value):
                print j
                try:
                    gross_tons = gross_tons + float(re.search(cm_re, chomped[j]).group(2))
                    net_tons = net_tons + float(re.search(cm_re, chomped[j]).group(3))
                except:
                    pass
        link_DF.loc[link_ID,str(rr)] = gross_tons
    #link_DF.to_csv('apple.csv')

link_DF.to_csv('apple.csv')