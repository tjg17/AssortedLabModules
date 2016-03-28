import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import time

# Definitions for GUI
def numericInputFrame(parent, label, tooltip, minimum, maximum, step, decimals):
    inputFrame = qt.QFrame(parent)
    inputFrame.setLayout(qt.QHBoxLayout())
    inputLabel = qt.QLabel(label, inputFrame)
    inputLabel.setToolTip(tooltip)
    inputFrame.layout().addWidget(inputLabel)
    inputSpinBox = qt.QDoubleSpinBox(inputFrame)
    inputSpinBox.setToolTip(tooltip)
    inputSpinBox.minimum = minimum
    inputSpinBox.maximum = maximum
    inputSpinBox.singleStep = step
    inputSpinBox.decimals = decimals
    inputFrame.layout().addWidget(inputSpinBox)
    return inputFrame, inputSpinBox

#
# VisualizeTimesteps
#

class VisualizeTimesteps(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "VisualizeTimesteps" # TODO make this more human readable by adding spaces
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
# VisualizeTimestepsWidget
#

class VisualizeTimestepsWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Patient Information"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    # Patient Number Box
    PatientNumberMethodFrame = qt.QFrame(self.parent)
    parametersFormLayout.addWidget(PatientNumberMethodFrame)
    PatientNumberMethodFormLayout = qt.QFormLayout(PatientNumberMethodFrame)
    PatientNumberIterationsFrame, self.PatientNumberIterationsSpinBox = numericInputFrame(self.parent,"Patient Number:","Tooltip",56,110,1,0)
    PatientNumberMethodFormLayout.addWidget(PatientNumberIterationsFrame)

    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = True
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    
    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = True

  def onApplyButton(self):
    logic = VisualizeTimestepsLogic()
    logic.run(str(int(self.PatientNumberIterationsSpinBox.value)))


#
# VisualizeTimestepsLogic
#

class VisualizeTimestepsLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def loadTimesteps(self,PatientNumber):
    """ Loads ARFI timestep volumes from file server. If inputs are not present, saves node variable as a string with missing filepath for error output
    """
    # Print to Slicer CLI
    print('Loading Ultrasound Inputs...'),
    start_time = time.time()

    # Load all timesteps
    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/loupas/avolume_ts1_737_370_366.nii.gz'):
        ts1 = slicer.util.getNode('avolume_ts1_737_370_366')
    else:
        ts1 = 'invivo/Patient'+PatientNumber+'/loupas/avolume_ts1_737_370_366.nii.gz'

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/loupas/avolume_ts2_737_370_366.nii.gz'):
        ts2 = slicer.util.getNode('avolume_ts2_737_370_366')
    else:
        ts2 = 'invivo/Patient'+PatientNumber+'/loupas/avolume_ts2_737_370_366.nii.gz'

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/loupas/avolume_ts3_737_370_366.nii.gz'):
        ts3 = slicer.util.getNode('avolume_ts3_737_370_366')
    else:
        ts3 = 'invivo/Patient'+PatientNumber+'/loupas/avolume_ts3_737_370_366.nii.gz'

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/loupas/avolume_ts4_737_370_366.nii.gz'):
        ts4 = slicer.util.getNode('avolume_ts4_737_370_366')
    else:
        ts4 = 'invivo/Patient'+PatientNumber+'/loupas/avolume_ts4_737_370_366.nii.gz'

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/loupas/avolume_ts5_737_370_366.nii.gz'):
        ts5 = slicer.util.getNode('avolume_ts5_737_370_366')
    else:
        ts5 = 'invivo/Patient'+PatientNumber+'/loupas/avolume_ts5_737_370_366.nii.gz'

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/loupas/avolume_ts6_737_370_366.nii.gz'):
        ts6 = slicer.util.getNode('avolume_ts6_737_370_366')
    else:
        ts6 = 'invivo/Patient'+PatientNumber+'/loupas/avolume_ts6_737_370_366.nii.gz'

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/loupas/avolume_ts7_737_370_366.nii.gz'):
        ts7 = slicer.util.getNode('avolume_ts7_737_370_366')
    else:
        ts7 = 'invivo/Patient'+PatientNumber+'/loupas/avolume_ts7_737_370_366.nii.gz'

    if slicer.util.loadVolume('/luscinia/ProstateStudy/invivo/Patient'+PatientNumber+'/loupas/avolume_ts8_737_370_366.nii.gz'):
        ts8 = slicer.util.getNode('avolume_ts8_737_370_366')
    else:
        ts8 = 'invivo/Patient'+PatientNumber+'/loupas/avolume_ts8_737_370_366.nii.gz'

    # print to Slicer CLI
    end_time = time.time()
    print('done (%0.2f s)') % float(end_time-start_time)

    return ts1, ts2, ts3, ts4, ts5, ts6, ts7, ts8


  def run(self, PatientNumber):
    """
    Run the actual algorithm
    """

    # Print to Slicer CLI
    logging.info('\n\n')
    start_time_overall = time.time() # start timer
    print('Expected Module Run Time: 30 seconds') # based on previous trials of the algorithm

    # Load Timesteps
    ts1, ts2, ts3, ts4, ts5, ts6, ts7, ts8 = self.loadTimesteps(PatientNumber)

    # Set Window Level for all Volumes
    for volumeNode in [ts1, ts2, ts3, ts4, ts5, ts6, ts7, ts8]:
      displayNode = volumeNode.GetDisplayNode()
      displayNode.SetAutoWindowLevel(0)
      displayNode.SetWindowLevel(110,50) # sets window level for viewing for loaded volumes

    logging.info('Processing completed')

    return True


class VisualizeTimestepsTest(ScriptedLoadableModuleTest):
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
    self.test_VisualizeTimesteps1()

  def test_VisualizeTimesteps1(self):
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
    logic = VisualizeTimestepsLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
