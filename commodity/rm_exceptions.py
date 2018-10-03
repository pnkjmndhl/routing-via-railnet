import arcpy
import pandas
import os

scenario_list = os.listdir('intermediate/')
scenario_list = [x.split('.csv')[0] for x in scenario_list if "_1" in x]
scenario_list = [x.replace('_1', '') for x in scenario_list]

# csv
link_shp = r"../GIS/alllinks.shp"
start_state_list = [27, 55, 26, 36]
end_state_list = [23, 50, 33, 17]
start_rr_except = [555, 777, 103, 712, 400, 802, 105]


def get_all_network_rrs():
    dummy = [[row.getValue("RR1"), row.getValue("RR2"), row.getValue("RR3"), row.getValue("RR4"), row.getValue("RR5")]
             for row in arcpy.SearchCursor(link_shp)]
    flat_list = list(set([x for sublist in dummy for x in sublist]))
    flat_list.remove(0)
    return flat_list


all_rrs = get_all_network_rrs()
RRs = [x for x in all_rrs if x not in start_rr_except]

for scenario in scenario_list:
    print("Working on " + scenario)
    commodity_file = r"intermediate/"+ scenario + "_1.csv"
    commodity_df = pandas.read_csv(commodity_file).dropna()
    # removal process
    current_column_names = commodity_df.columns
    commodity_df['O'] = (commodity_df['ONode'] / 1000).astype(int)
    commodity_df['D'] = (commodity_df['DNode'] / 1000).astype(int)
    commodity_df1_satisfying = commodity_df[((commodity_df.O.isin(start_state_list) & commodity_df.D.isin(
        end_state_list)) | (commodity_df.D.isin(start_state_list) & commodity_df.O.isin(
        end_state_list))) & commodity_df.startRR.isin(RRs)]
    print commodity_df1_satisfying
    print "{0} satisfying records removed.".format(len(commodity_df1_satisfying))
    commodity_df.drop(commodity_df1_satisfying.index, axis=0, inplace=True)
    print "{0} records remain.".format(len(commodity_df))
    commodity_df = commodity_df[current_column_names]
    commodity_df.to_csv(r"intermediate/"+ scenario + "_2.csv")
