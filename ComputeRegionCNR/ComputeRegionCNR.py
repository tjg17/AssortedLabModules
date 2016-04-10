import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import time

#
# ComputeRegionCNR
#

class ComputeRegionCNR(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ComputeRegionCNR" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# ComputeRegionCNRWidget
#

class ComputeRegionCNRWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector1 = slicer.qMRMLNodeComboBox()
    self.inputSelector1.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector1.selectNodeUponCreation = True
    self.inputSelector1.addEnabled = False
    self.inputSelector1.removeEnabled = False
    self.inputSelector1.noneEnabled = False
    self.inputSelector1.showHidden = False
    self.inputSelector1.showChildNodeTypes = False
    self.inputSelector1.setMRMLScene( slicer.mrmlScene )
    self.inputSelector1.setToolTip( "Pick the input greyscale volume to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector1)

    #
    # input volume 2 selector
    #
    self.inputSelector2 = slicer.qMRMLNodeComboBox()
    self.inputSelector2.nodeTypes = ( ("vtkMRMLLabelMapVolumeNode"), "" )
    self.inputSelector2.selectNodeUponCreation = True
    self.inputSelector2.addEnabled = False
    self.inputSelector2.removeEnabled = False
    self.inputSelector2.noneEnabled = False
    self.inputSelector2.showHidden = False
    self.inputSelector2.showChildNodeTypes = False
    self.inputSelector2.setMRMLScene( slicer.mrmlScene )
    self.inputSelector2.setToolTip( "Pick the input segmentation to the algorithm." )
    parametersFormLayout.addRow("Input Lesion: ", self.inputSelector2)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector1.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.inputSelector2.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector1.currentNode() and self.inputSelector2.currentNode()

  def onApplyButton(self):
    logic = ComputeRegionCNRLogic()
    logic.run(self.inputSelector1.currentNode(), self.inputSelector2.currentNode())

#
# ComputeRegionCNRLogic
#

class ComputeRegionCNRLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def CloneVolumeNode(self,inputNode,newNodeName):
    """ Clones the input volume node to give an output node with the same parameters but a new name
    given by the newNodeName parameter """

    # Print to Slicer CLI
    print('Cloning input to get output volume...'),
    start_time = time.time()

    # Logic for cloning volume
    volumesLogic = slicer.modules.volumes.logic()
    clonedVolumeNode = volumesLogic.CloneVolume(slicer.mrmlScene, inputNode, newNodeName)

    # Print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return clonedVolumeNode

  def SymmetricTransform(self, *ModuleInputs):
    """ Performs L/R symmetry transform with [-1 1 1 1] diagonal entries on inputs
    """
    # Print to Slicer CLI
    print('Applying L/R symmetry transform...'),
    start_time = time.time()

    # Create inverting transform matrix
    symmetry_transform = vtk.vtkMatrix4x4()
    symmetry_transform.SetElement(0,0,-1) # put a -1 in 1st entry of diagonal of matrix

    # Apply transform to all input nodes
    for ModuleInput in ModuleInputs:
        ModuleInput.ApplyTransformMatrix(symmetry_transform)

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def ComputeLabelStatistics(self, grayscaleNode, inputlabelNode):
    """ Computes label statistics for input label node on grayscale volume (mean, std, volume, etc)
    """  
    # Print to Slicer CLI
    print('Computing Label Statistics...'),
    start_time = time.time()

    # resample the label to the space of the grayscale if needed
    volumesLogic = slicer.modules.volumes.logic()
    warnings = volumesLogic.CheckForLabelVolumeValidity(grayscaleNode, inputlabelNode)
    if warnings != "":
      if 'mismatch' in warnings:
        inputlabelNode = volumesLogic.ResampleVolumeToReferenceVolume(inputlabelNode, grayscaleNode)

    # Set up Stat accumulator
    stataccum = vtk.vtkImageAccumulate()
    stataccum.SetInputConnection(inputlabelNode.GetImageDataConnection())
    stataccum.Update()
    InputLabelValue = int(stataccum.GetMax()[0])

    # logic copied from slicer3 LabelStatistics
    thresholder = {}
    thresholder = vtk.vtkImageThreshold()
    thresholder.SetInputConnection(inputlabelNode.GetImageDataConnection())
    thresholder.SetInValue(1)
    thresholder.SetOutValue(0)
    thresholder.ReplaceOutOn()
    thresholder.ThresholdBetween(InputLabelValue,InputLabelValue)
    thresholder.SetOutputScalarType(grayscaleNode.GetImageData().GetScalarType())
    thresholder.Update()

    # use vtk's statistics class with the binary labelmap as a stencil
    stencil = vtk.vtkImageToImageStencil()
    stencil.SetInputConnection(thresholder.GetOutputPort())
    stencil.ThresholdBetween(1, 1)
    stencil.Update()

    # this.InvokeEvent(vtkLabelStatisticsLogic::LabelStatsInnerLoop, (void*)"0.5")
    stat1 = vtk.vtkImageAccumulate()
    stat1.SetInputConnection(grayscaleNode.GetImageDataConnection())
    stat1.SetStencilData(stencil.GetOutput())
    stat1.Update()

    ### List of possible label stats available ###
    # cubicMMPerVoxel = reduce(lambda x,y: x*y, inputlabelNode.GetSpacing())
    # ccPerCubicMM = 0.001
    # labelStats["Labels"].append(i)
    # labelStats[i,"Index"] = i
    # labelStats[i,"Count"] = stat1.GetVoxelCount()
    # labelStats[i,"Volume mm^3"] = labelStats[i,"Count"] * cubicMMPerVoxel
    # labelStats[i,"Volume cc"] = labelStats[i,"Volume mm^3"] * ccPerCubicMM
    # labelStats[i,"Min"] = stat1.GetMin()[0]
    # labelStats[i,"Max"] = stat1.GetMax()[0]
    # labelStats[i,"Mean"] = stat1.GetMean()[0]
    # labelStats[i,"StdDev"] = stat1.GetStandardDeviation()[0]

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    # Return desired stats to variables
    return stat1.GetMean()[0], stat1.GetStandardDeviation()[0]

  def ThresholdScalarVolume(self, inputVolume, newLabelVal):
    """ Thresholds nonzero values on an input labelmap volume to the newLabelVal number while leaving all 0 values untouched
    """
    # Print to Slicer CLI
    print('Changing Label Value...'),
    start_time = time.time()

    # Run the slicer module in CLI
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': inputVolume.GetID(), 'ThresholdType': 'Above', 'ThresholdValue': 0.5, 'OutsideValue': newLabelVal} 
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)
    
    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def run(self, inputVolume, inputLabel):

    """
    Run the actual algorithm
    """

    # Starting Print to Slicer CLI
    logging.info('\n\nProcessing started')
    start_time = time.time() # start timer
    print('Expected Algorithm Time: 3 seconds\n') # based on previous trials of the algorithm

    # Create segmentation volume as clone of input label
    symmetricLabel = self.CloneVolumeNode(inputLabel,'symmetricLabel')

    # Transform Symmetric Label using L/R symmetry and Change Label Value to 25
    self.SymmetricTransform(symmetricLabel)
    self.ThresholdScalarVolume(symmetricLabel,  25)

    # Compute Means and Std from LabelStatistics Module
    ROI_mean, ROI_std = self.ComputeLabelStatistics(inputVolume,inputLabel)
    symmetricROI_mean, symmetricROI_std = self.ComputeLabelStatistics(inputVolume,symmetricLabel)

    # Print CNR
    #print "Lesion Mean: ",
    print ROI_mean
    #print "Lesion STD: ",
    print ROI_std
    #print "Symmetric Area Mean: ",
    print symmetricROI_mean
    #print "Symmetric Area STD: ",
    print symmetricROI_std
    #print "Computed CNR: ",
    print abs(ROI_mean-symmetricROI_mean)/symmetricROI_std
    

    # Ending Print to Slicer CLI
    end_time = time.time()
    logging.info('\nProcessing completed')
    print('Overall Algorithm Time: % 0.1f seconds') % float(end_time-start_time)

    return True


class ComputeRegionCNRTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ComputeRegionCNR1()

  def test_ComputeRegionCNR1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = ComputeRegionCNRLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
