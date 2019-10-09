import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import json
#import pdb
#pdb.set_trace()

#
# visuThreeD
#

class visuThreeD(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "visuThreeD" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Wieke Prummel (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """

""" # replace with organization, grant and thanks.
    #self.JSON_DIR = os.path.dirname(os.path.realpath(__file__)) + '/Resources/json/'
#
# visuThreeDWidget
#

class visuThreeDWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  #def __init__(self, parent = None):

    # To avoid the overhead of importing SimpleITK during application
    # startup, the import of SimpleITK is delayed until it is needed.
    #global sitk
    #import SimpleITK as sitk
    # global sitkUtils
    # import sitkUtils

    # if not parent:
    #   self.parent = slicer.qMRMLWidget()
    #   self.parent.setLayout(qt.QVBoxLayout())
    #   self.parent.setMRMLScene(slicer.mrmlScene)
    # else:
    #   self.parent = parent
    # self.layout = self.parent.layout()
    # if not parent:
    #   self.setup()
    #   self.parent.show()


    # jsonFiles =(self.JSON_DIR+"*.json")
    # jsonFiles.sort(key=lambda x: os.path.basename(x))

    # self.jsonFilters = []

    # for fname in jsonFiles:
    #   try:
    #     with open(fname, "r") as json_file:
    #       data = json_file.read()
    #       # if j["name"] in dir(sitk):
    #       #   self.jsonFilters.append(j)
    #       # else:
    #       #   if j["itk_module"] in sitk.Version().ITKModulesEnabled():
    #       #     import sys
    #       #     sys.stderr.write("Unknown SimpleITK class \"{0}\".\n".format(j["name"]))
    #   except Exception as e:
    #     import sys
    #     sys.stderr.write("Error while reading \"{0}\". Exception: {1}\n".format(fname, e))


    # self.filterParameters = None
    # self.logic = None


  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # input json file search box
    #
    # self.searchBox = ctk.ctkSearchBox()
    # fileFormLayout.addRow("Search:", self.searchBox)
    # self.searchBox.connect("textChanged(QString)", self.onSearch)

    # # file selector
    # self.fileSelector = qt.QComboBox()
    # fileFormLayout.addRow("Filter:", self.fileSelector)

    # # add all the files listed in the json files
    # for idx,j in enumerate(self.jsonFilters):
    #   name = j["name"]
    #   self.fileSelector.addItem(name, idx)

    # # connections
    # self.fileSelector.connect('currentIndexChanged(int)', self.onFileSelect)

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
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)
    
    #
    # directory button
    #
    #
    self.inputJson = ctk.ctkDirectoryButton()
    #self.inputJson.setText("choose json_file directory")
    self.inputJson.browse()
    #self.inputJson.directory(".json")

    # threshold value
    #
    self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
    self.imageThresholdSliderWidget.singleStep = 0.1
    self.imageThresholdSliderWidget.minimum = -100
    self.imageThresholdSliderWidget.maximum = 100
    self.imageThresholdSliderWidget.value = 0.5
    self.imageThresholdSliderWidget.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    parametersFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.coord = []
    self.x = []
    self.y = []
    self.z = []
    self.logic = visuThreeDLogic()
    #self.applyButton.connect('clicked(bool)', self.logic.store_CoordInList(self.x,self.y,self.z))
    self.applyButton.connect('clicked(bool)', self.onApplyButton)  
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.inputJson.connect('clicked(bool)', self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode() #and self.inputJson.clicked()

  def onApplyButton(self):
    logic = visuThreeDLogic()
    #enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    #imageThreshold = self.imageThresholdSliderWidget.value
    # logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)
    #logic.store_CoordInList(self.x,self.y,self.z)
    #self.logic.ThreeD_View()
    logic.run()

#
# visuThreeDLogic
#

class visuThreeDLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def __init__(self):
    self.coord = []
    self.x = []
    self.y = []
    self.z = []
    self.segmentationNode = slicer.vtkMRMLSegmentationNode()
  
  #Access json data
  def decode_coord(self, dct):
    if "coord" in dct:
      return (dct["coord"])
    return dct

  def decode_hierarchy(self, dct):
    if "VisuHierarchy" in dct:
      return (dct["VisuHierarchy"])
    return dct

  #read json file
  def read_JsonFile(self, coord):
    with open("/work/wprummel/Tools/Test-files/Connectome_3D_Visualization/nodeGraph_3D.json", "r") as json_file:
      #Stores the json data in a dictionnary
      # data = json.load(json_file)
      self.data = json_file.read()
      self.coord = json.loads(self.data, object_hook=self.decode_coord)
      #self.newfile = json_file.copy()
    return self.coord

  #Store x,y,z coordinates in separate lists 
  def store_CoordInList(self,x, y, z):
    coord = self.read_JsonFile(self.coord)
    for i in range(len(self.coord)):
      x = self.x.append(self.coord[i][0])
      y = self.y.append(self.coord[i][1])
      z = self.z.append(self.coord[i][2])
    return x, y, z

    # liste_x = []
    # liste_y = []
    # liste_z = []
    # for i in range(len(x)):
    #   delta_x = x[i]
    #   delta_y = y[i]
    #   delta_z = z[i]
    #   liste_x.append(delta_x)
    #   liste_y.append(delta_y)
    #   liste_z.append(delta_z)

  def ThreeD_View(self, segmentationNode):
    #Create Segmentation node that stores a set of segments
    #self.segmentationNode = slicer.vtkMRMLSegmentationNode()
    slicer.mrmlScene.AddNode(self.segmentationNode)
    #enable node display
    self.segmentationNode.CreateDefaultDisplayNodes()
    #if we define a master volume loaded by the user
    # self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)
    #Create nodes
    #coord=[]
    append=vtk.vtkAppendPolyData()
    for i in range(len(self.x)):
      #coord.append([liste_x[i], liste_y[i], liste_z[i]])
      self.coord.append(self.store_CoordInList(self.x[i], self.y[i], self.z[i]))
      #print coord
      threeDNode = vtk.vtkSphereSource()
      threeDNode.SetCenter(self.coord[i])
      threeDNode.SetRadius(7)
      threeDNode.Update()
      append.AddInputData(threeDNode.GetOutput())
    append.Update()
    threeDNodeId = self.segmentationNode.AddSegmentFromClosedSurfaceRepresentation(append.GetOutput(), "Node",[0.0,1.0,1.0])
    segmentationDisplayNode = self.segmentationNode.GetDisplayNode()
    segmentationDisplayNode.SetSegmentVisibility(threeDNodeId, True)

  def run(self):
    self.store_CoordInList(self.x,self.y,self.z)
    self.ThreeD_View(self.segmentationNode)

class visuThreeDTest(ScriptedLoadableModuleTest):
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
    self.test_visuThreeD1()

  def test_visuThreeD1(self):
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

    # self.delayDisplay("Starting the test")
    # #
    # # first, get some data
    # #
    # import SampleData
    # SampleData.downloadFromURL(
    #   nodeNames='FA',
    #   fileNames='FA.nrrd',
    #   uris='http://slicer.kitware.com/midas3/download?items=5767')
    # self.delayDisplay('Finished with download and loading')

    # volumeNode = slicer.util.getNode(pattern="FA")
    # logic = visuThreeDLogic()
    # self.assertIsNotNone( logic.hasImageData(volumeNode) )
    # self.delayDisplay('Test passed!')
    import json
    #Access json data
    def decode_coord(dct):
      if "coord" in dct:
        return (dct["coord"])
      return dct

    def decode_hierarchy(dct):
      if "VisuHierarchy" in dct:
        return (dct["VisuHierarchy"])
      return dct

    def decode_name(dct):
      if "name" in dct:
        return (dct["name"])
      return dct

    #read json file
    #def read_JsonFile():
    coord = []
    node_tag = []
    with open("/work/wprummel/Tools/Test-files/Connectome_3D_Visualization/nodeGraph_3D.json", "r") as json_file:
      #Stores the json data in a dictionnary
      # data = json.load(json_file)
      data = json_file.read()
      coord = json.loads(data, object_hook=decode_coord)
      node_tag = json.loads(data, object_hook=decode_name)

#     chart = vtk.vtkChartXYZ()
# view = vtk.vtkContextView()
# view.GetRenderWindow().SetSize(400,300)
# view.GetScene().AddItem(chart)
# chart.SetGeometry(vtk.vtkRectf(75.0,20.0,250,260))

# table = vtk.vtkTable()
# arrX=vtk.vtkFloatArray()
# arrX.SetName("x")
# table.AddColumn(arrX)
# arrY=vtk.vtkFloatArray()
# arrY.SetName("y")
# table.AddColumn(arrY)
# arrZ=vtk.vtkFloatArray()
# arrZ.SetName("z")
# table.AddColumn(arrZ)


    X=10
    Y=10
    Z=10
    # x = [-38.65, 41.37]
    # y = [-5.68,-8.21]
    # z = [50.94,52.09]
    x = []
    y = []
    z = []
    for i in range(len(coord)):
      x.append(coord[i][0])
      y.append(coord[i][1])
      z.append(coord[i][2])

    liste_x = []
    liste_y = []
    liste_z = []
    for i in range(len(x)):
      delta_x = x[i]
      delta_y = y[i]
      delta_z = z[i]
      liste_x.append(delta_x)
      liste_y.append(delta_y)
      liste_z.append(delta_z)

# numNodes=3
# r=4
# points_x=[]
# table.SetNumberOfRows(numNodes)
# for i in range(1):
#   table.SetValue(i, 0, liste_x[i])
#   table.SetValue(i, 1, liste_y[i]) 
#   table.SetValue(i, 2, liste_z[i]) 

    #Create Segmentation node that stores a set of segments
    segmentationNode = slicer.vtkMRMLSegmentationNode()
    slicer.mrmlScene.AddNode(segmentationNode)
    #enable node display
    segmentationNode.CreateDefaultDisplayNodes()
    #if we define a master volume loaded by the user
    # segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)

    #Create nodes
    #coord=[]
    append=vtk.vtkAppendPolyData()
    for i in range(len(liste_x)):
      coord.append([liste_x[i], liste_y[i], liste_z[i]])
      threeDNode = vtk.vtkSphereSource()
      threeDNode.SetCenter(coord[i])
      threeDNode.SetRadius(7)
      threeDNode.Update()
      append.AddInputData(threeDNode.GetOutput())

    append.Update()
    threeDNodeId = segmentationNode.AddSegmentFromClosedSurfaceRepresentation(append.GetOutput(), "Node",[0.0,1.0,1.0])

    segmentationDisplayNode = segmentationNode.GetDisplayNode()
    segmentationDisplayNode.SetSegmentVisibility(threeDNodeId, False)
