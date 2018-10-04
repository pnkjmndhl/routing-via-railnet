from rail import *
import arcpy

arcpy.env.overwriteOutput = True

# 1: 'RR-Code'
# 2: 'Commod.',
# 3: 'TrainCost/hr'
# 4: 'Cost/gross-ton-mile',
# 5: 'terminal-processing-cost/car,fixed',
# 6: 'terminal-cost/car-hr',
# 7: 'transfer-cost/car',
# 8: 'car-payload',
# 9: 'car-tare-wt',
# 10: 'Gross Car Weight',
# 11: 'Cars per Train',
# 12: 'Gross Train Weight'

add = 50  # 10 columns for cost Attribute file [additional value for empty rail]
cost_xl_df = pandas.ExcelFile(cost_xl).parse(cost_xl_sheet)

cost_xl_df.columns = [['1', '13', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']]
cost_xl_df = cost_xl_df[['1', '2', '3', '4', '5', '6', '7', '8', '9', '12']]

cost_xl_df['1'] = cost_xl_df['1'].astype(int)
cost_xl_df['2'] = cost_xl_df['2'].astype(int)

# add the railroads not in the cost file (short-line 6 AA, is used as a sample for all unknown values)
sample_shortline_df = cost_xl_df[cost_xl_df['1'] == 6]  # extracting 6
all_rrs_in_cost = set(cost_xl_df['1'].astype(int).tolist())
rrs_to_add = set(get_network_rrs()) - all_rrs_in_cost

rrs_to_add_df = pandas.DataFrame()
for rrs in rrs_to_add:
    sample_shortline_df['1'] = rrs
    rrs_to_add_df = rrs_to_add_df.append(sample_shortline_df, ignore_index=True)

cost_xl_df = cost_xl_df.append(rrs_to_add_df, ignore_index=True)

# empty cost_xl_df default values
empty_rail_cost_df = cost_xl_df.copy(deep=True)
empty_rail_cost_df['2'] = empty_rail_cost_df['2'] + add  # 2: 'Commod.',
empty_rail_cost_df['3'] = 520.93  # 3: 'TrainCost/hr'
empty_rail_cost_df['4'] = 0.055  # 4: 'Cost/gross-ton-mile',
empty_rail_cost_df['5'] = 95.67  # 5: 'terminal-processing-cost/car,fixed',
empty_rail_cost_df['6'] = 1.14  # 6: 'terminal-cost/car-hr',
empty_rail_cost_df['7'] = 157.92  # 7: 'transfer-cost/car',
empty_rail_cost_df['8'] = cost_xl_df['9']  # 8: 'car-payload' (since payload = tare wt)
empty_rail_cost_df['9'] = 0  # 9: 'car-tare-wt' = 0

empty_rail_cost_df['12'] = cost_xl_df['9'] * cost_xl_df['12'] / (cost_xl_df['8'] + cost_xl_df['9'])

cost_xl_df = cost_xl_df.append(empty_rail_cost_df).reset_index()[['1', '2', '3', '4', '5', '6', '7', '8', '9', '12']]

# changing the formatting
cost_xl_df['1'] = cost_xl_df['1'].astype(int)
cost_xl_df['2'] = cost_xl_df['2'].astype(int)

cost_xl_df['1'] = cost_xl_df['1'].map('{:3d}'.format)
cost_xl_df['2'] = cost_xl_df['2'].map('{:5d}'.format)
cost_xl_df['3'] = cost_xl_df['3'].map('{:10.2f}'.format)
cost_xl_df['4'] = cost_xl_df['4'].map('{:10.2f}'.format)
cost_xl_df['5'] = cost_xl_df['5'].map('{:10.2f}'.format)
cost_xl_df['6'] = cost_xl_df['6'].map('{:10.2f}'.format)
cost_xl_df['7'] = cost_xl_df['7'].map('{:10.2f}'.format)
cost_xl_df['8'] = cost_xl_df['8'].map('{:5.1f}'.format)
cost_xl_df['9'] = cost_xl_df['9'].map('{:5.1f}'.format)
cost_xl_df['12'] = cost_xl_df['12'].map('{:10.1f}'.format)

# combine all the columns to one
cost_xl_df = cost_xl_df[['1', '2', '3', '4', '5', '6', '7', '8', '9', '12']].apply(
    lambda x: '  {}{}{}{}{}{}{}{}{}{}'.format(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9]), axis=1)

cost_xl_df.to_csv(r"output\cost.dat", index=False)

print("OPERATION SUCCESSFULL. cost.dat written")
