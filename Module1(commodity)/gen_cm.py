#calculate quantities for empty rails and aggregate if necessary
import pandas
import numpy
import os

scenario_list = os.listdir('intermediate/')
scenario_list = [x.split('.csv')[0] for x in scenario_list if "OD3" in x]
scenario_list = [x.replace('OD3','') for x in scenario_list]


#parameters
add = 50 # for empty
no_of_commodity = 12

for scenario in scenario_list:

   #inputs from files
   ODNEW = pandas.read_csv(r'intermediate\OD3'+scenario+'.csv')
   FIPStoNodes = pandas.read_csv(r'intermediate\FIPStonodeshp.csv')

   def splitwidth(widths):
      borders = numpy.cumsum([0] + widths)
      split = list(zip(borders[:-1], borders[1:]))
      return split

   #using cost.dat
   CA = pandas.read_fwf(r'..\Module2(cost)\output\cost.dat' , colspecs = splitwidth([5,5,10,10,10,10,10,5,5,10]), header = None)
   #CA.columns = [['RR-Code','Commod.','TrainCost/hr','Cost/gross-ton-mile','terminal-processing-cost/car,fixed','terminal-cost/car-hr','transfer-cost/car','car-payload','car-tare-wt','Gross Car Weight','Cars per Train','Gross Train Weight']]
   CA.columns = [['1','2','3','4','5','6','7','8','9','12']]
   CA = CA[['1','2','8','9']]


   def GetAvgPayload(comm):
      payloadCommList = CA[(CA['2'] == comm)]['8'].tolist()
      return sum(payloadCommList)/len(payloadCommList)

   def GetAvgTareWt(comm):
      tareWtCommList = CA[(CA['2'] == comm)]['9'].tolist()
      return sum(tareWtCommList)/len(tareWtCommList)

   #removing unnecessary columns
   ODEMPTY = ODNEW.copy()

   #creating empty commodity payload &tareweight
   for i in range(1,no_of_commodity + 1):
      EmptyAttributesDF = pandas.DataFrame( { '1': [0], '2' : [i], '8': [GetAvgPayload(i)], '9': [GetAvgTareWt(i)] } )
      CA = CA.append(EmptyAttributesDF)

   CA['VlookUP'] = (CA['2']).astype(int).astype(str) + "," + (CA['1']).astype(int).astype(str)
   CA = CA.set_index('VlookUP')


   ODEMPTY['VlookUP'] = ODEMPTY['comm'].astype(int).astype(str) + "," + (ODEMPTY['startRR']).astype(int).astype(str)
   ODEMPTY['payload'] = ODEMPTY['VlookUP'].map(CA['8'])
   ODEMPTY['tareWt'] = ODEMPTY['VlookUP'].map(CA['9'])
   ODEMPTY['quantity'] = ODEMPTY['quantity']*1.0 / ODEMPTY['payload'] * ODEMPTY['tareWt']
   ODEMPTY.comm = ODEMPTY.comm + add #commodity for emptys is 90 + original
   ODEMPTY['startRR'] = 0 #emptys can come back using any railroads
   ODEMPTY['ONode'] = ODEMPTY['DFIPS'].map(FIPStoNodes.set_index('FIPS').nodeshpID)  #ONode and DNode were swapped
   ODEMPTY['DNode'] = ODEMPTY['OFIPS'].map(FIPStoNodes.set_index('FIPS').nodeshpID)

   #ODEMPTY.to_csv("intermediate\odempty.csv")

   #appending to the original file
   ODNEW = ODNEW[['OFIPS', 'DFIPS','comm', 'ONode', 'DNode', 'startRR', 'quantity']]
   ODEMPTY = ODEMPTY[['OFIPS', 'DFIPS','comm', 'ONode', 'DNode', 'startRR', 'quantity']]
   ODNEW = ODNEW.append(ODEMPTY)

   #aggregate after append
   ODNEW = pandas.pivot_table(ODNEW, values='quantity', index=['comm', 'ONode', 'DNode', 'startRR'], aggfunc=numpy.sum)
   ODNEW = ODNEW.reset_index()
   print("Aggregating Successful")

   #remove -99 in ONODE or DNODE (those are FIPS codes not found in FIPS.shp)
   ODNEW = ODNEW[ODNEW.ONode != -99]
   ODNEW = ODNEW[ODNEW.DNode != -99]

   #remove the ones with 0 quantity
   ODNEW = ODNEW[ODNEW.quantity != 0]

   ODNEW.to_csv("intermediate\cm2011.csv")


   #remove same origin and destination
   ODNEW = ODNEW [ ODNEW.ONode != ODNEW.DNode].reset_index() #if equal, its removed
   print("Removing records with same origin and destination")
   ODNEW = ODNEW[['ONode', 'DNode', 'comm', 'startRR', 'quantity']]
   ODNEW = ODNEW.sort_values(['ONode', 'DNode', 'comm', 'startRR'], ascending=[True, True, True, True])


   #convert all the required data to integer since mapping for integers only works for integers
   ODNEW.ONode = ODNEW.ONode.astype(int)
   ODNEW.DNode = ODNEW.DNode.astype(int)

   ODNEW = ODNEW.replace(numpy.nan, 0, regex=True)
   ODNEW.startRR = ODNEW.startRR.astype(int)

   ODNEW['comm'] = ODNEW['comm'].map('{:5d}'.format)
   ODNEW['ONode'] = ODNEW['ONode'].map('{:5d}'.format)
   ODNEW['DNode'] = ODNEW['DNode'].map('{:5d}'.format)
   ODNEW['quantity'] = ODNEW['quantity'].map('{:10.1f}'.format)
   ODNEW['startRR'] = ODNEW['startRR'].map('{:5d}'.format)

   # combine all the columns to one
   ODNEW = ODNEW[['comm', 'ONode', 'DNode', 'quantity', 'startRR']].apply(lambda x : '{}{}{}{}{}'.format(x[0],x[1],x[2],x[3],x[4]), axis=1)


   #ODNEW2 = ODNEW[50000:]
   ODNEW.to_csv(r"output\cm"+scenario+".dat", index = False)






