# Dragonfly_scripts
Scripts for Dragonfly. Python, batch processing, visualization/rendering.

## Extract_fragments
Export snapshots and/or volumes and/or movies of parts of a dataset cropped from a multiROI

Context: a channel and a multiROI already open (with the same geometry) ; a single 3D view in the layout. 

Principle: Get each ROI from the multiROI, dilate it, crop the dataset, render the cropped dataset and produce output.

To run this script:
 - open Dragonfly console
 - import sys
 - sys.path.append([Location of the script])
 - cd [Location of the script]
 - import Extract_fragments
 - Extract_fragments.main(screenshots: Boolean, volume: Boolean, movie: Boolean, output directory: String)

 Hints: The visual properties of the initial dataset are transfered to the cropped datasets, so make sure to choose them wisely before starting the script.