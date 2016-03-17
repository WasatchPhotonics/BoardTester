REM Copy the current combined_log.csv file to the Wasatch Photonics Z: drive
REM Rename it in place based on the current computer hostname
REM
REM Designed to be called every N minutes from windows task scheduler

FOR /F "usebackq" %%i IN (`hostname`) DO SET MYVAR=%%i

copy "C:\projects\BoardTester\scripts\combined_log.csv" "Z:\common\Long_Term_Testing\%MYVAR%_combined_log.csv"


