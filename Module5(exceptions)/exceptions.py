import pandas
import numpy

#inputs from files
exceptions = 'Exceptions.xlsx'
linkexc = pandas.ExcelFile(exceptions).parse("link")
transexc = pandas.ExcelFile(exceptions).parse("transfer")

#change format
linkexc = linkexc[['ID', 'RR', 'comm', 'direction', 'costpertrainhr', 'costpertonmile']]
linkexc.ID = linkexc.ID.astype(int)
linkexc.RR = linkexc.RR.astype(int)
linkexc.comm = linkexc.comm.astype(int)
linkexc.direction = linkexc.direction.astype(int)
linkexc.costpertonmile = linkexc.costpertonmile.astype(float)

transexc = transexc[['ID','RR1',	'RR2','comm','cost']]
transexc.ID = transexc.ID.astype(int)
transexc.RR1 = transexc.RR1.astype(int)
transexc.RR2 = transexc.RR2.astype(int)
transexc.comm = transexc.comm.astype(int)
transexc.cost = transexc.cost.astype(float)

linkexc['ID'] = linkexc['ID'].map('{:5d}'.format)
linkexc['RR'] = linkexc['RR'].map('{:5d}'.format)
linkexc['comm'] = linkexc['comm'].map('{:5d}'.format)
linkexc['direction'] = linkexc['direction'].map('{:5d}'.format)
linkexc['costpertrainhr'] = linkexc['costpertrainhr'].map('{:10.2f}'.format)
linkexc['costpertonmile'] = linkexc['costpertonmile'].map('{:10.2f}'.format)

transexc['ID'] = transexc['ID'].map('{:5d}'.format)
transexc['RR1'] = transexc['RR1'].map('{:5d}'.format)
transexc['RR2'] = transexc['RR2'].map('{:5d}'.format)
transexc['comm'] = transexc['comm'].map('{:5d}'.format)
transexc['cost'] = transexc['cost'].map('{:10.2f}'.format)

linkexc = linkexc[['ID', 'RR', 'comm', 'direction', 'costpertrainhr', 'costpertonmile']].apply(lambda x : '{}{}{}{}{}{}'.format(x[0],x[1],x[2],x[3],x[4],x[5]), axis=1)  
transexc = transexc[['ID','RR1',	'RR2','comm','cost']].apply(lambda x : '{}{}{}{}{}'.format(x[0],x[1],x[2],x[3],x[4]), axis=1)

linkexc.to_csv("link.exc", index = False)
transexc.to_csv("transfer.exc", index = False)

