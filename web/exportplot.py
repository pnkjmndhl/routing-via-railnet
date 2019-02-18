import os
import pyautogui
import time
import subprocess

#export to folder
os.startfile("railqgis.qgs")
time.sleep(10) #wait for sometime to open qgisfile
pyautogui.hotkey('alt', 'w')
pyautogui.press('q')
pyautogui.press('enter')
for i in range(5):
    pyautogui.press('tab')
pyautogui.press('enter')
time.sleep(25) #wait for sometime to prepare the file
print("Export Folder Updated.")

#get foldername
cwd = os.getcwd()
os.chdir('./openlayers_api')
name_list = os.listdir(".")
folder_name = sorted(name_list, key=os.path.getmtime)[-1]
os.chdir(cwd)
print("Export Folder name: {0}".format(folder_name))


#open bash and send
os.startfile("C:\Users\pankaj\AppData\Local\Programs\Git\git-bash.exe")
time.sleep(3) #wait for sometime to prepare the file
pyautogui.typewrite('scp -r openlayers_api/'+folder_name+'/* pdahal@hydra4.eecs.utk.edu:~/webhome/')
pyautogui.press('enter')
time.sleep(2) #wait for sometime to open qgisfile
pyautogui.typewrite('MNipd!2#FirIrIIn')
pyautogui.press('enter')

time.sleep(15) #wait tille the files are copied
#change the attributes to 777
pyautogui.typewrite('ssh pdahal@hydra4.eecs.utk.edu')
pyautogui.press('enter')
time.sleep(2) #wait for sometime to open qgisfile
pyautogui.typewrite('MNipd!2#FirIrIIn')
pyautogui.press('enter')
time.sleep(2) #wait for sometime to open qgisfile
pyautogui.typewrite('chmod -R 777 webhome/')
pyautogui.press('enter')
pyautogui.typewrite('~.') #exit ssh connection








