BoardTester usage

broaster, visualize and camids are designed to help you evaluate the
efficacy of line scan and area scan cameras. This helps you change ‘it
works’ into statistical data on the quality and quantity of the imagery.

For example, you use the broaster to collect line scan camera data from
a Wasatch Photonics WP 785 class device:

```python boardtester/broaster.py -i 100 -d “Laser on, integration time 100”```

This will produce output like:

![broaster screenshot](/docs/narr_broaster.png "broaster narrative screenshot")


In the examples below, the data was collected in 5 groups of 100 scans
each. 

Now you want to determine if any of the data was dropped. That is, did
any attempt to acquire data from the device result in an python
exception, USB protocol timeout, or other error?

```python boardtester/visualize.py -g gaps -n “exam_results”```


![broaster screenshot](/docs/narr_visualizegaps.png "broaster narrative screenshot")


The ‘gaps’ visualization module process all of the logged pixel data for
an average on a per-line basis. The plot of these average values will be
shown with gaps for each of the missing data points. In the graph above,
there are no missing data points, and the average data value for the CCD
is well within the noise level of the detector.  The image below shows a
cropped version of the opposite conditions:


![broaster screenshot](/docs/narr_visualizewidegaps.png "broaster narrative screenshot")


You can see the gaps in the data around position 550, 630, and 750 among
others. Also note the wide variance in average signal levels.


Further analysis is possible with the heatmap visualization:


```python boardtester/visualize.py -g heatmap -n “exam_results”```


![broaster screenshot](/docs/narr_heatmap.png "broaster narrative screenshot")


The ‘heatmap’ visualization reads in every pixel value stored in all of
the exam_log files created for each run of the broaster. This data is
represented as a 2-dimensional heatmap using the guiqwt imagedialog.
Hover your mouse over the heatmap while holding down the alt key to see
live updates in the cross-section window top the top and right of the
image. Click the image, and then select the start and end values in the
contast adjustment tool to highlight specific data ranges within the
image. 

For example, the following image was produced by narrowing the contrast
adjustment minimum and maximum range, then right clicking the image and
turning off image aspect ratio lock. The image was then zoomed into a
region around the peak. Make sure to click the ‘>>’ button in the top
cross section toolbar and turn off auto-scaling to have the axis match
with the image.

![broaster screenshot](/docs/narr_heatmapcontrast.png "broaster narrative screenshot")

Look for patterns in the data that can be difficult to pickup through
standard statistical measurements, such as precessing or intermittent
hot pixels.  Try different colors maps such as ‘prism’ for alternate
visualizations.

