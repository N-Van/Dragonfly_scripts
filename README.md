# Dragonfly_scripts
Scripts for Dragonfly. Python, batch processing, visualization/rendering.

## Extract_fragments
Works with [Dragonfly 3D World 2024.1](https://dragonfly.comet.tech "Dragonfly"), the 3D image processing program by Comet Technologies Canada Inc.
(probably works with 2025.1. Didn't try)

Export 3D rendered snapshots and/or volumes and/or movies of parts of a dataset cropped using a MultiROI.
Case use: many small segmented objects whose 3D representation is of interest (e.g. bone fragments in a funeray urn)

**Context**: a single channel and a single MultiROI already open (with the same geometry) ; a single 3D view in the layout. 

**Principle**: The script extracts each element from the multiROI to an ROI, dilates it, crops the dataset, renders the cropped dataset and produces output.

To run this script:
 - Copy `Export_fragments.py` to a folder of your choice.
 - Launch Dragonfly 2024.1.
 - Load 1 MultiROI and 1 dataset.
 - Set a 3D view as the only window.
 - Open Dragonfly console and type the following lines:.
 - `import sys`
 - `sys.path.append([script folder])`
 - `cd [script folder]`
 - `import Extract_fragments`
 - `Extract_fragments.main(screenshots: Boolean, volume: Boolean, movie: Boolean, output directory: String)`
 - Keep your fingers crossed that the movie maker doesn’t crash, and be patient if you have many objects to process.

`screenshots` (0 or 1): export 8 screenshots for each ROI at different angles.

`volume` (0 or 1): export each cropped dataset to a single ORSObject file for further inspection.

`movie` (0 or 1): export a small 3D animation for each object.

`output directory` (string): where everything will be saved.

**Hints**: The visual properties of the initial dataset are transfered to the cropped datasets, so make sure to choose them wisely before starting the script.

**Disclaimer**: use at your own risk, not intended for clinical use, safety-critical applications etc.