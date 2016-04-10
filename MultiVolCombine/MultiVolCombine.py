import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import time
from vtk.util import numpy_support
import numpy as np

#
# MultiVolCombine
#

class MultiVolCombine(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "MultiVolCombine" # TODO make this more human readable by adding spaces
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
# MultiVolCombineWidget
#

class MultiVolCombineWidget(ScriptedLoadableModuleWidget):
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
    # input volume 1 selector
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
    self.inputSelector1.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume 1: ", self.inputSelector1)

    #
    # input volume 2 selector
    #
    self.inputSelector2 = slicer.qMRMLNodeComboBox()
    self.inputSelector2.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector2.selectNodeUponCreation = True
    self.inputSelector2.addEnabled = False
    self.inputSelector2.removeEnabled = False
    self.inputSelector2.noneEnabled = False
    self.inputSelector2.showHidden = False
    self.inputSelector2.showChildNodeTypes = False
    self.inputSelector2.setMRMLScene( slicer.mrmlScene )
    self.inputSelector2.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume 2: ", self.inputSelector2)

    #
    # input volume 3 selector
    #
    self.inputSelector3 = slicer.qMRMLNodeComboBox()
    self.inputSelector3.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector3.selectNodeUponCreation = True
    self.inputSelector3.addEnabled = False
    self.inputSelector3.removeEnabled = False
    self.inputSelector3.noneEnabled = False
    self.inputSelector3.showHidden = False
    self.inputSelector3.showChildNodeTypes = False
    self.inputSelector3.setMRMLScene( slicer.mrmlScene )
    self.inputSelector3.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume 3: ", self.inputSelector3)

    #
    # input volume 4 selector
    #
    self.inputSelector4 = slicer.qMRMLNodeComboBox()
    self.inputSelector4.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector4.selectNodeUponCreation = True
    self.inputSelector4.addEnabled = False
    self.inputSelector4.removeEnabled = False
    self.inputSelector4.noneEnabled = False
    self.inputSelector4.showHidden = False
    self.inputSelector4.showChildNodeTypes = False
    self.inputSelector4.setMRMLScene( slicer.mrmlScene )
    self.inputSelector4.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume 4: ", self.inputSelector4)

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
    self.applyButton.enabled = self.inputSelector1.currentNode()

  def onApplyButton(self):
    logic = MultiVolCombineLogic()
    logic.run(self.inputSelector1.currentNode(), self.inputSelector2.currentNode(),
              self.inputSelector3.currentNode(), self.inputSelector4.currentNode())

#
# MultiVolCombineLogic
#

class MultiVolCombineLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() == None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def SetOutputPixelValues(self, outputVolumeNode, outputNumpyarray):
    """This method sums the pixel values at all locations in the two input volume nodes 
    and assigns the summed values to the outputVolumeNode. All inputs and output volumes
    must be the same size"""

    # Print to Slicer CLI
    print('Setting output pixels...'),
    start_time = time.time()

    # Convert Numpy array to VTK (use double since will need double for SetTuple1() later)
    VTK_data = numpy_support.numpy_to_vtk(num_array=outputNumpyarray, deep=True, array_type=vtk.VTK_UNSIGNED_INT)

    # Get scalar data for output image
    outputImageScalars = outputVolumeNode.GetImageData().GetPointData().GetScalars()

    # List Comprehension to fill all values
    [outputImageScalars.SetTuple1(Index,VTK_data.GetTuple1(Index)) for Index in xrange(outputImageScalars.GetNumberOfTuples())]

    # Print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

  def NumpyCombinePixelValues(self, inputVolumeNode1, inputVolumeNode2, inputVolumeNode3, inputVolumeNode4):
    """This method gets Numpy array information from the input volumes and combines 
    the pixel information to give an output numpy array. All input volumes must 
    be the same size"""

    # Print to Slicer CLI
    print('Combining input pixels...'),
    start_time = time.time()

    # Get Image Data for Input Volumes
    imdata1 = inputVolumeNode1.GetImageData()
    imdata2 = inputVolumeNode2.GetImageData()
    imdata3 = inputVolumeNode3.GetImageData()
    imdata4 = inputVolumeNode4.GetImageData()

    # Get Dimensions of First Input (all inputs should match)
    x,y,z   = imdata1.GetDimensions()

    # Get scalar data for all inputs
    scalars1 = imdata1.GetPointData().GetScalars()
    scalars2 = imdata2.GetPointData().GetScalars()
    scalars3 = imdata3.GetPointData().GetScalars()
    scalars4 = imdata4.GetPointData().GetScalars()

    ## Make Numpy Arrays from Scalar Data
    array1 = numpy_support.vtk_to_numpy(scalars1)
    array2 = numpy_support.vtk_to_numpy(scalars2)
    array3 = numpy_support.vtk_to_numpy(scalars3)
    array4 = numpy_support.vtk_to_numpy(scalars4)

    # Combine Arrays (must divide before summing or will add to more than 256 and wrap around values)

    # Averaging
    outputNumpyarray1 = array1/4+array2/4+array2/4+array3/4

    # Projection
    max12 = np.maximum(array1,array2)
    max34 = np.maximum(array3,array4)
    outputNumpyarray2 = np.maximum(max12,max34)


    # Print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return outputNumpyarray1, outputNumpyarray2

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

  def run(self, inputVolume1, inputVolume2, inputVolume3, inputVolume4):
    """
    Run the actual algorithm
    """

    # Starting Print Statements
    logging.info('\n\nProcessing started')
    print('Expected Algorithm Time: 33 seconds') # based on previous trials of the algorithm
    start_time_overall = time.time() # start timer    

    # Combine Pixel Values in input images into Numpy Array
    outputNumpyarray1, outputNumpyarray2 = self.NumpyCombinePixelValues(inputVolume1, inputVolume2, inputVolume3, inputVolume4)

    # Set output volume pixels using combined Numpy array
    outputVolume1 = self.CloneVolumeNode(inputVolume1,'ts2334') # Create output volume as clone of input volume 1
    self.SetOutputPixelValues(outputVolume1,outputNumpyarray1)

    outputVolume2 = self.CloneVolumeNode(inputVolume1,'proj_2345') # Create output volume as clone of input volume 1
    self.SetOutputPixelValues(outputVolume2,outputNumpyarray2)

    # Ending Print Statements
    end_time_overall = time.time()
    logging.info('Processing completed')
    print('Overall Algorithm Time: % 0.1f seconds') % float(end_time_overall-start_time_overall)

    return True


class MultiVolCombineTest(ScriptedLoadableModuleTest):
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
    self.test_MultiVolCombine1()

  def test_MultiVolCombine1(self):
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
    logic = MultiVolCombineLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')