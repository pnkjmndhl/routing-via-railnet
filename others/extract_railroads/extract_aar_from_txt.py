import re
import pandas as pd

dataframe = pd.DataFrame({'Name':[], 'AARCode':[], 'ABBR':[]})

#regex = re.compile("(\D+) (\w{2,4}) (\d{3}\s)")
regex = re.compile("([A-Za-z0-9()&.,\/\-\'\– ]*) (\w{2,5}) (\d{3}\s)")


with open("new 1.txt") as f:
   for line in f:
      result = regex.search(line)
      new = pd.DataFrame({'Name':[result.group(1)], 'AARCode':[result.group(2)], 'ABBR': [result.group(3).split('\n')[0]]})
      dataframe = dataframe.append(new)

dataframe.to_csv("AARCode.csv", ignore_index=True)
	