python 1gen_transfershp_from_xl.py
if errorlevel 1 pause
python 2snap_plot_gen_transferfile.py
if errorlevel 1 pause
copy output/network.xfr C:\Users\pankaj\Desktop\RAIL\Netdata\
if errorlevel 1 pause