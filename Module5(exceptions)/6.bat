call updatefiles.bat

python exceptions.py
if errorlevel 1 pause

cp link.exc ../outputs/link.exc
cp transfer.exc ../outputs/transfer.exc

