# AssortedLabModules

This 3D slicer extension contains various modules used for visualizing and combining ARFI timestep information.

The VisualizeTimesteps module loads ARFI timestep information for a given Patient Number from file server and sets up the Window/Level so that each volume can be visualized. The volumes can then be scrolled through in the slice pane to see differences between them.

The SetVolumeScalars module combines pixel intensity information from input volumes of equal size to give an output volume containing information from each of the input volumes. An example is shown below with an ARFI ultrasound (left) and Bmode ultrasound (center) pixel values being averaged to give the CombinedVolume seen on the right image.

![alt tag](http://i66.tinypic.com/95vf9f.png)


