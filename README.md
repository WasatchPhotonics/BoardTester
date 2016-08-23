BoardTester - collect data with automated hardware power cycling



broaster 

    The Board Roaster. Turn on a board, get data, turn off board.
    Repeat and analyze the results.

![broaster screenshot](/docs/broaster.png "broaster screenshot")

camids 

    IDS uEye USB camera tester. Use a relay to simulate the plugging in
    of a IDS camera, start the uEye cockpit software, take a screenshot.
    Repeat. Store the data for later analysis. Also can use custom Large
    Animal OCT software as camera control.


![camids screenshot](/docs/camids.png "camids screenshot")


process

    Process the results. Create text and graphical summaries of test
    results from the broaster or camids.


visualize

    Provide a gui for visualizing broaster results.

![visualize screenshot](/docs/visualize.png "visualize screenshot")

visualize Installation:
   
    For details on how to install guiqwt in a virtual environment that
    closely matches that provided by python xy 2.7.10, see the file: 
   
https://github.com/nharringtonwasatch/BoardTester/blob/master/docs/guiqwt_pythonxy_match.md


    On first installation, make sure to extract the offset/gain data in
    into the testing folder. Specifically, download the file at the
    location: http://goo.gl/w3ytRJ into the folder:
```
boardtester/test/known_results/
```

    Extract the zip file, and Make sure the output directory has the 
    format:

```
known_results/PRLW047_sorted_20140730/PRL_Offset_90_Gain_0_254.csv
known_results/PRLW047_sorted_20140730/PRL_Offset_91_Gain_0_254.csv
known_results/PRLW047_sorted_20140730/PRL_Offset_92_Gain_0_254.csv
...
```

BoardTester\TemperatureLogger.py

    Acquire readings rapidly over a time frame, save the average to disk
    over a much longer time frame. This allows for realtime
    visualization of 100's of temperature and power events per second,
    while also recording instantaneous and long term trends to disk.
    Broadcasts events over the network to allow for non-interruption
    required changes in data collection and visualization procedures.

scripts\dsh_checker.py

    Power cycle the spectrometer, start the Dash version on the Desktop.
    Change integration time, toggle cooling, and collection a
    screenshot. Requires manually reprocessing to detect failure rates.
