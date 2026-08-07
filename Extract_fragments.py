""" Export snapshots and/or volumes and/or movies of parts of a dataset cropped from a multiROI
# Context: a channel and a multiROI already open (with the same geometry) ; a single 3D view in the layout. 
# Principle: Get each ROI from the multiROI, dilate it, crop the dataset, render the cropped dataset and produce output.
# Hints: Visual properties of the initial dataset are transfered to each of the cropped datasets. Make sure to choose them wisely.
# To run this script:
# - open Dragonfly console
# - import sys
# - sys.path.append([Location of the script])
# - cd [Location of the script]
# - import Extract_fragments
# - Extract_fragments.main(screenshots: Boolean, volume: Boolean, movie: Boolean, output directory: String)
##

## TODO
# - reset to initial state after after each roi snapshot
"""

import os
import sys
from ORSModel import ROI, MultiROI, Channel, View, Image, VisualChannel, ArrayUnsignedLong, Camera, Vector3, Visual, StructuredGrid, Managed
from OrsHelpers.multiroilabelhelper import MultiROILabelHelper
from OrsHelpers.roihelper import ROIHelper
from OrsHelpers.datasethelper import DatasetHelper
from OrsHelpers.managedhelper import ManagedHelper
from OrsHelpers.refreshHelper import RefreshHelper
from OrsHelpers.layoutHelper import LayoutHelper
from OrsHelpers.layoutpropertieshelper import LayoutPropertiesHelper
from OrsHelpers.viewLogger import ViewLogger
from OrsPlugins.orsqtlayout import OrsQtLayout
from OrsLibraries.workingcontext import WorkingContext
from COMWrapper.ORS_def import CxvView_Mode
from OrsPythonPlugins.OrsVolumeROITools.OrsVolumeROITools import OrsVolumeROITools
from OrsPythonPlugins.OrsDatasetCropper.OrsDatasetCropper import OrsDatasetCropper

def main(screenshots, volume, movie, out_dir):
    # Get 1st MultiROI and 1st Channel in the workspace
    mroi, dataset = get_mroi_and_dataset()

    # Get ROIs
    labels = ArrayUnsignedLong()
    labels = mroi.getNonEmptyLabels(labels)
    print(f"Dataset X, Y, Z size: {dataset.getXSize()}, {dataset.getYSize()}, {dataset.getZSize()}")
    print(f"Nb of labels: {labels.getSize()}")
    
    # Get 3d view and layout name
    layout_full_name, view_3d = get_3d_view()
    for label in labels:
        print(f"Label: {label}")
        roi = MultiROILabelHelper.extractROIForLabel(mroi, label) 
        print(f"ROI size: {roi.getVoxelCount(0)}")
        roi.setTitle(f"ROI_{label}")

        # Dilate and crop the dataset with the dilated ROI
        OrsVolumeROITools.dilate(roi, kernelShape='circle', kernelDim=3, kernelSize=3)
        cropped_dataset = Channel()
        cropped_dataset = dataset.getAsChannelFromROI(roi, cropped_dataset)
        
        # Crop the dataset according to the bounding box of the roi
        box = roi.getBoundingBox(0)
        _ = OrsDatasetCropper.cropFromBox(cropped_dataset, False, box, tMin=0, tMax=0)
        print(f"cropped_dataset X, Y, Z size: {cropped_dataset.getXSize()}, {cropped_dataset.getYSize()}, {cropped_dataset.getZSize()}")

        # Hide all objects except cropped_dataset
        hide_everything_except_dataset(view_3d, cropped_dataset)

        # Show and center cropped_dataset
        DatasetHelper.setIsVisibleIn2D(cropped_dataset, view_3d, True)
        DatasetHelper.setIsVisibleIn3D(cropped_dataset, view_3d, True)
        DatasetHelper.fitToView(cropped_dataset, view_3d) # Not in the API

        # Export screenshots
        if (screenshots):
            export_screenshots(view_3d, layout_full_name, label, roi, cropped_dataset, out_dir)
        
        # Export volume
        if (volume):
            cropped_dataset.atomicSave(os.path.join(out_dir, f"Object_{label}_vol.ORSObject"), False, 1)
                
        # Export movie
        if (movie):
            export_movie(cropped_dataset, view_3d, label, out_dir)

        # Cleanup - anything else to remove?
        cropped_dataset.deleteObject()
        roi.deleteObject()
        
    # TODO: reset everything, return to the same state/context/whatever as before the script was called
    return

# Get the 3D view and the layout name (only one scene, one layout, one 3D view)
def get_3d_view():
    layout_of_scenes = LayoutHelper.getTopLayoutOfContext(None)
    layout_full_name = layout_of_scenes.getGenealogicalName()
    scene_layouts = layout_of_scenes.getAllChildLayout()
    scene_layout = scene_layouts[0]
    views = scene_layout.getAllChildViews()
    view_3d = views[0]
    view_3d.setViewMode(CxvView_Mode.CXVVIEW_MODE_3D)
    return layout_full_name, view_3d

def hide_everything_except_dataset(view_3d: View, cropped_dataset: Channel):
    visualChannels = view_3d.getAllVisibleChildrenOfClass(VisualChannel.getClassNameStatic())
    for vc in visualChannels:
        channel = vc.getFirstParentOfClass(Channel.getClassNameStatic())
        if channel != cropped_dataset:
            DatasetHelper.setIsVisibleIn2D(channel, view_3d, False)
            DatasetHelper.setIsVisibleIn3D(channel, view_3d, False)
    return

def export_screenshots(view_3d, layout_full_name, label, roi, cropped_dataset, out_dir):
    viewLogger = ViewLogger()
    angle = 45
    rotationCenter = roi.getCenterOfMass(0)
    rotationAxis = Vector3(1,1,1)
    DatasetHelper.fitToView(cropped_dataset, view_3d)
    for i in range(6):
        # Rotate camera
        camera = view_3d.getCamera()
        camera.rotateAroundAxis(rotationAxis, rotationCenter, angle)
        viewLogger.setCameraFromLayoutGenealogicalName(layout_full_name, camera)
        view_3d.saveScreenshot(os.path.join(out_dir, f"Object_{label}_screenshot_{i*angle}.png"), scale=1.0)
    return

def export_movie(cropped_dataset, view_3d, label, out_dir):
    try:
        orsQtLayout = OrsQtLayout()
        orsQtLayout.openMovieMaker()
        
        DatasetHelper.setIsVisibleIn2D(cropped_dataset, view_3d, True)
        DatasetHelper.setIsVisibleIn3D(cropped_dataset, view_3d, True)
        DatasetHelper.fitToView(cropped_dataset, view_3d) # Not in the API
        
        orsQtLayout.forceDraw()
        orsQtLayout.addMovieRotationKeyFrameInCurrentView(3, 360, 3, False)            
        orsQtLayout.addMovieRotationKeyFrameInCurrentView(1, 360, 3, False)

        orsQtLayout.exportAVIInCurrentView(os.path.join(out_dir, f"Object_{label}_3Danim.avi"), width=1280, height=720, fps=20, startFrame=0, endFrame=-1)
        orsQtLayout.deleteMovieInCurrentView()
        orsQtLayout.closeMovieMaker()
        return
    except:
        print("Problem with the movie maker")
        orsQtLayout.closeMovieMaker()
        return

def get_mroi_and_dataset(): # ! Only first occurrence of channel and multiROI classes
    mroi = Managed.getAllInstancesOf(MultiROI.getClassNameStatic())[0]
    dataset = Managed.getAllInstancesOf(Channel.getClassNameStatic())[0]
    return mroi, dataset

if __name__ == "__main__":
    screenshots = sys.argv[1] # Export screenshots at different angles
    volume = sys.argv[2] # Export ORS object
    movie = sys.argv[3] # Export 3D animation
    out_dir = sys.argv[4] # Where?
    main(screenshots, volume, movie, out_dir)