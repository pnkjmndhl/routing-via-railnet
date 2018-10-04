# calculate quantities for empty rails and aggregate if necessary
from rail import *
import pandas
import numpy
import os

scenario_list = os.listdir('intermediate/')
scenario_list = [x.split('.csv')[0] for x in scenario_list if "_2" in x]
scenario_list = [x.replace('_2', '') for x in scenario_list]

# parameters
add = 50  # for empty
no_of_commodity = 12


def split_width(widths):
    borders = numpy.cumsum([0] + widths)
    split = list(zip(borders[:-1], borders[1:]))
    return split


def get_average_payload(comm):
    all_payloads_list = attributes_for_full[(attributes_for_full['2'] == comm)]['8'].tolist()
    return sum(all_payloads_list) / len(all_payloads_list)


def get_average_tare_weight(comm):
    all_tare_weight_list = attributes_for_full[(attributes_for_full['2'] == comm)]['9'].tolist()
    return sum(all_tare_weight_list) / len(all_tare_weight_list)


# using cost.dat
attributes_for_full = pandas.read_fwf(cost_dat,
                                      colspecs=split_width([5, 5, 10, 10, 10, 10, 10, 5, 5, 10]),
                                      header=None)
# attributes_for_full.columns = [['RR-Code','Commod.','TrainCost/hr','Cost/gross-ton-mile',
# 'terminal-processing-cost/car,fixed','terminal-cost/car-hr','transfer-cost/car','car-payload',
# 'car-tare-wt','Gross Car Weight','Cars per Train','Gross Train Weight']]

attributes_for_full.columns = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '12']]
attributes_for_full = attributes_for_full[['1', '2', '8', '9']]

for scenario in scenario_list:
    # inputs from files
    base_df = pandas.read_csv(r'intermediate/' + scenario + '_2.csv')
    empty_base_df = base_df.copy()
    # creating empty commodity payload & tare weight
    for i in range(1, no_of_commodity + 1):
        attributes_for_empty = pandas.DataFrame(
            {'1': [0], '2': [i], '8': [get_average_payload(i)], '9': [get_average_tare_weight(i)]})
        attributes_for_full = attributes_for_full.append(attributes_for_empty)

    empty_base_df['comm'] = empty_base_df['comm'].astype(int)
    empty_base_df['startRR'] = empty_base_df['startRR'].astype(int)

    empty_base_df = pandas.merge(base_df, attributes_for_full, left_on=['startRR', 'comm'], right_on=['1', '2'],
                                 how='left')
    empty_base_df['quantity'] = empty_base_df['quantity'] * 1.0 / empty_base_df['8'] * empty_base_df['9']
    empty_base_df.comm = empty_base_df.comm + add  # commodity for emptys is 90 + original
    empty_base_df['startRR'] = 0  # emptys can come back using any railroads
    empty_base_df = empty_base_df.rename(index= str, columns = {'DNode':'ONode', 'ONode':'DNode'})
    # empty_base_df['ONode'] = empty_base_df['DFIPS'].map(
    #     FIPStoNodes.set_index('FIPS').nodeshpID)  # ONode and DNode were swapped
    # empty_base_df['DNode'] = empty_base_df['OFIPS'].map(FIPStoNodes.set_index('FIPS').nodeshpID)

    # appending to the original file
    base_df = base_df[['comm', 'ONode', 'DNode', 'startRR', 'quantity']]
    empty_base_df = empty_base_df[['comm', 'ONode', 'DNode', 'startRR', 'quantity']]

    base_df = base_df.append(empty_base_df)


    # aggregate after append
    print("Aggregating commodity " + scenario )
    base_df = pandas.pivot_table(base_df, values='quantity', index=['comm', 'ONode', 'DNode', 'startRR'],
                                 aggfunc=numpy.sum)
    base_df = base_df.reset_index()



    base_df = base_df[base_df.quantity != 0]  # remove the ones with 0 quantity
    base_df = base_df[base_df.ONode != base_df.DNode].reset_index()  # # remove same origin and destination
    base_df.to_csv("intermediate\cm2011.csv")

    base_df = base_df[['ONode', 'DNode', 'comm', 'startRR', 'quantity']]
    #base_df = base_df.sort_values(['ONode', 'DNode', 'comm', 'startRR'], ascending=[True, True, True, True])

    # convert all the required data to integer since mapping for integers only works for integers
    base_df.ONode = base_df.ONode.astype(int)
    base_df.DNode = base_df.DNode.astype(int)

    base_df = base_df.replace(numpy.nan, 0, regex=True)
    base_df.startRR = base_df.startRR.astype(int)

    base_df['comm'] = base_df['comm'].map('{:5d}'.format)
    base_df['ONode'] = base_df['ONode'].map('{:5d}'.format)
    base_df['DNode'] = base_df['DNode'].map('{:5d}'.format)
    base_df['quantity'] = base_df['quantity'].map('{:10.1f}'.format)
    base_df['startRR'] = base_df['startRR'].map('{:5d}'.format)

    # combine all the columns to one
    base_df = base_df[['comm', 'ONode', 'DNode', 'quantity', 'startRR']].apply(
        lambda x: '{}{}{}{}{}'.format(x[0], x[1], x[2], x[3], x[4]), axis=1)
    base_df.to_csv(r"output/" + scenario + ".dat", index=False)
