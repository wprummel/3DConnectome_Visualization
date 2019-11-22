import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import json, ast
import re
import vtkSegmentationCorePython
import numpy as np
from json_extract_properties import *
#import json_extract_properties
import csv
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
    #self.parent.packages = "json_extract_properties.py"
    #json_extract_properties.read_csvFile(self.user_csvFile)
    self.parent.contributors = ["Wieke Prummel (University of North Carolina)"] # replace with "Firstname Lastname (Organization)"
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

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    #json_extract_properties.read_csvFile(self.user_csvFile)
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
    #self.regioncheckbox()
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
    # input file selector
    #
    #self.inputJson = ctk.ctkFileDialog()
    # self.inputJson = ctk.ctkPathLineEdit()
    #self.inputJson = ctk.ctkPathLineEdit.Files
    # #self.inputJson.Files
    # #self.inputJson.browse()
    # #self. inputJson.setCurrentFileExtension()
    # #self.inputJson.setSettingKey(".json file")

    # #get path
    #self.path = ctk.ctkPathLineEdit.currentPath
    #jfile = open(self.path)
    # self.inputJson.comboBox()
    # self.inputJson.addCurrentPathToHistory()
    #myFile = open(path)
    #self.inputJson.setText("choose json_file directory")
    #self.inputJson.browse()
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

    #
    # File Push Button
    #
    # self.fileButton = qt.QPushButton("Import .json")
    # self.fileButton.toolTip = "Load your file"
    # self.fileButton.enabled = False
    # parametersFormLayout.addRow(self.fileButton)
    
    #
    # Checkable header button node regions
    #
    #self.nodeButton = ctk.ctkCheckablePushButton()

    #
    # Node Selector Area
    #
    self.nodeselectCollapsibleButton = ctk.ctkCollapsibleButton()
    self.nodeselectCollapsibleButton.text = "Selection of Node Region"
    self.layout.addWidget(self.nodeselectCollapsibleButton)
    # Layout within the collapsible button
    self.nodeselectFormLayout = qt.QFormLayout(self.nodeselectCollapsibleButton)
    
    # Search Box to filter regions to display
    self.searchLayout = qt.QHBoxLayout()
    self.nodeselectFormLayout.addRow('Search:', self.searchLayout)
    self.regionSearchBox = ctk.ctkSearchBox()
    self.regionSearchBox.placeholderText = "search region"
    self.searchLayout.addWidget(self.regionSearchBox)

    #
    # Region checkbox Area
    #
    self.regioncheckCollapsibleButton = ctk.ctkCollapsibleButton()
    self.regioncheckCollapsibleButton.text = "Check region to visualize"
    self.layout.addWidget(self.regioncheckCollapsibleButton)
    # Layout within the collapsible button
    self.regioncheckFormLayout = qt.QFormLayout(self.regioncheckCollapsibleButton)

    # CheckableComboBox
    self.checkSearchLayout = qt.QHBoxLayout()
    #self.name = qt.QModelIndex()
    self.regioncheckFormLayout.addRow('Search:', self.checkSearchLayout)
    self.checkComboBox = ctk.ctkCheckableComboBox()
    self.checkSearchLayout.addWidget(self.checkComboBox)
    

    # Add buttons to select all or no region
    self.buttonsLayout = qt.QHBoxLayout()
    self.nodeselectFormLayout.addRow('Toggle Regions:', self.buttonsLayout)
    self.calculateAllregionsButton = qt.QPushButton('All Regions')
    self.calculateAllregionsButton.toolTip = 'Select all region.'
    self.calculateAllregionsButton.enabled = True
    self.buttonsLayout.addWidget(self.calculateAllregionsButton)
    self.calculateAllFilteredregionsButton = qt.QPushButton('All Filtered Regions')
    self.calculateAllFilteredregionsButton.toolTip = 'Select all  filtered region.'
    self.calculateAllFilteredregionsButton.enabled = True
    self.buttonsLayout.addWidget(self.calculateAllFilteredregionsButton)
    self.calculateNoregionsButton = qt.QPushButton('No Regions')
    self.calculateNoregionsButton.toolTip = 'Select no region.'
    self.calculateNoregionsButton.enabled = True
    self.buttonsLayout.addWidget(self.calculateNoregionsButton)
    self.calculateNoFilteredregionsButton = qt.QPushButton('No filtered Regions')
    self.calculateNoFilteredregionsButton.toolTip = 'Select no filtered region.'
    self.calculateNoFilteredregionsButton.enabled = True
    self.buttonsLayout.addWidget(self.calculateNoFilteredregionsButton)

    self.regionsLayout = qt.QHBoxLayout()
    self.nodeselectFormLayout.addRow('Regions:', self.regionsLayout)
    #QButtonGroup class provides a container to organize groupss of button widgets
    # Invisible way to group buttons together
    self.regionsButtonGroup = qt.QButtonGroup(self.regionsLayout)
    self.regionsButtonGroup.exclusive = False

    # logic = visuThreeDLogic()
    # self.path_to_json ='/work/wprummel/Tools/Test-files/Connectome_3D_Visualization/nodeGraph_3D.json'
    # self.nodeGraphArray = []
    # with open(self.path_to_json, "r") as dct:
    #     self.nodeGraphArray = json.load(dct)
    # self.regions = logic.readName_JsonFile(self.nodeGraphArray)


    self.regions = ['seed.left.frontal.', 'seed.right.cingulate.', 'seed.right.occipital.']
    #create a checkbox for each region
    #Store de region buttons in a dictionnary
    self.regionButtons = {}
    for r in self.regions:

        self.regionButtons[r] = qt.QCheckBox(r)
        self.regionButtons[r].checked = False
        #print self.regionButtons['seed left frontal']
        # add regions that are selected by default
        if r == 'seed left frontal':

            self.regionButtons[r].checked = True

        self.regionsButtonGroup.addButton(self.regionButtons[r])
        self.regionsLayout.layout().addWidget(self.regionButtons[r])
        # set Margins, param (alignement left, separation with toggleRegions, separation btw checkbox, separation with Size)
        self.regionsLayout.setContentsMargins(0, 5, 10, 5)
        # set the ID to be the index of this region in the list
        self.regionsButtonGroup.setId(self.regionButtons[r], self.regions.index(r))
    #return regionButtons

    #
    # Threshold node size
    #
    self.nodeThresholdSliderWidget = ctk.ctkSliderWidget()
    self.nodeThresholdSliderWidget.singleStep = 0.1
    self.nodeThresholdSliderWidget.minimum = 0
    self.nodeThresholdSliderWidget.maximum = 10
    self.nodeThresholdSliderWidget.value = 0.5
    self.nodeThresholdSliderWidget.setToolTip("Set threshold size value for computing the node size.")
    self.nodeselectFormLayout.addRow("Size:", self.nodeThresholdSliderWidget)

    #
    # Node Size and colorbar thresholding Area
    #
    self.colorbarCollapsibleButton = ctk.ctkCollapsibleButton()
    self.colorbarCollapsibleButton.text = "Node Size and Color thresholding"
    self.layout.addWidget(self.colorbarCollapsibleButton)
    # Layout within the collapsible button
    self.regioncheckFormLayout = qt.QFormLayout(self.colorbarCollapsibleButton)

    self.ColorTable = slicer.qMRMLColorTableComboBox()
    self.ColorTable.nodeTypes = ["vtkMRMLColorTableNode"]
    self.ColorTable.addEnabled = True
    self.ColorTable.removeEnabled = True
    self.ColorTable.noneEnabled = True
    self.ColorTable.showHidden = True
    self.ColorTable.setMRMLScene( slicer.mrmlScene )
    self.regioncheckFormLayout.addRow("Input color map: ", self.ColorTable)



    # self.lookupTable = vtk.vtkLookupTable()
    # self.lookupTable.SetNumberOfTableValues(20)
    # self.lookupTable.Build()
    # self.ColorTable.currentColorNodeID()
    # for i in range(0, 20):
    #     colorbar =self.ColorTable.nodeFromIndex()
    #     self.lookupTable.SetTableValue(i, colorbar)


    # self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    # self.inputSelector.selectNodeUponCreation = True
    # self.inputSelector.addEnabled = False
    # self.inputSelector.removeEnabled = False
    # self.inputSelector.noneEnabled = False
    # self.inputSelector.showHidden = False
    # self.inputSelector.showChildNodeTypes = False
    # self.inputSelector.setMRMLScene( slicer.mrmlScene )
    # self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    # parametersFormLayout.addRow("Input Volume: ", self.inputSelector)


    #
    # connections
    #
    self.coord = []
    self.x = []
    self.y = []
    self.z = []
    self.index = []
    self.position = []
    self.visu = []
    self.logic = visuThreeDLogic()
    #self.nodeButton.connect('mouseclick(bool)', self.onMouseClick)
    #self.applyButton.connect('clicked(bool)', self.logic.store_CoordInList(self.x,self.y,self.z))
    self.applyButton.connect('clicked(bool)', self.onApplyButton)  
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.regionsButtonGroup.connect('clicked()', self.regioncheckbox())
    self.regionsButtonGroup.buttonClicked.connect(self.onRegionSelect)
    #self.calculateAllregionsButton.connect(self.onSelectAllRegionsButton)
    self.regionsButtonGroup.buttonReleased.connect(self.cleanup)
    #singal is TextChanged
    self.regionSearchBox.connect("textChanged(QString)", self.onSearch)
    #self.ColorTable.connect("currentNodeChanged(vtkMRMLColorTableNode*)", "setColorNode(vtkMRMLColorTableNode*)")
    #self.ColorTable.connect("setColorNode(vtkMRMLColorTableNode*)", self.ColorTable.currentNode())
    
    #currentColorNodeID = self.mrmlManager().GetColorNodeID()
    #currentColorNode = slicer.mrmlScene.GetNodeByID( currentColorNodeID )
    #if currentColorNode:
    #  self.__colorTableComboBox.setCurrentNode( currentColorNode )

    # self.displayNode =vtk.vtkMRMLScalarVolumeNode()
    # if self.displayNode:
    #     self.ColorTable.setCurrentNode(self.displayNode)

    #self.ColorTable.connect("currentNodeChanged(vtkMRMLNode*)", "setColorNode(vtkMRMLNode*)")
    self.ColorTable.connect("currentNodeChanged(vtkMRMLNode*)", self.onColorClicked)
    #self.ColorTable.setCurrentNodeID("vtkMRMLColorTableNode *")
    
    # self.regionButtons = self.regionsButtonGroup.buttons()
    # for regionButton in self.regionButtons:
    #     regionButton.connect('clicked(bool)', self.regioncheckbox()) #self.onRegionSelect(r))
    #self.regionsButtonGroup.connect('clicked(bool)', self.regioncheckbox())

    #self.fileButton.connect('clicked(bool)', self.onFileLoad)
    #self.inputJson.connect('browse()', self.onSelect)
    
    # Add vertical spacer
    self.layout.addStretch(1)
    # Refresh Apply button state
    self.onSelect()
    #self.onFileLoad()

    #self.regioncheckbox()

    #
    # Get the brain regions dynamically
    #

  def regioncheckbox(self,r):
    for r in self.regions:
        print ("Thank you! ")
    #self.regionsButtonGroup.connect('toggled(bool)', self.onApplyButton)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode() #and self.inputJson.clicked()

  # def onMouseClick(self):
  #   self.nodeButton.enabled = self.nodeButton.mousePressEvent()

  def onColorClicked(self):
    global colorMap
    colorMap = slicer.qMRMLColorPickerWidget()
    colorMap.currentColorNode()
    print colorMap
    self.logic.run_all()

    # displayNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLColorTableNode')
    # displayNode.SetScene(slicer.mrmlScene)
    # ColorTableLabel = slicer.util.getNode('vtkMRMLColorTableNodeRainbow')
    # #displayNode.SetAndObserveColorNodeID(ColorTableLabel.GetID())
    # slicer.mrmlScene.AddNode(ColorTableLabel)
    # #label.SetAndObserveDisplayNodeID(ColorTableLabel.GetID())
    # for color in ['vtkMRMLColorTableNode']:
    #     slicer.app.layoutManager().sliceWidget(color)
    #     #slicer.app.layoutManager().sliceWidget(color).GetSliceCompositeNode().SetLabelVolumeID(label.GetID())
    #     #slicer.app.layoutManager().sliceWidget(color).GetSliceCompositeNode().SetLabelOpacity(0.6)











    # self.lookupTable = vtk.vtkLookupTable()
    # self.lookupTable.SetNumberOfTableValues(20)
    # self.lookupTable.Build()
    #self.ColorTable.Build(self.lookupTable)
    #self.ColorTable.currentColorNodeID()



    # if not self.ColorTable == "":
    #   #self.ColorTable.GetColor()
    #   self.ColorTable.selectCommand = self.addStructure
    # else:
    #   #self.ColorTable.colorNode = colorNode
    #   self.ColorTable.parent.populate()
    #   self.ColorTable.parent.show()
    #   self.ColorTable.parent.raise_()


    
    #self.mrmlScene.SetColorNodeID( self.ColorTable.currentNodeId)
    
    #self.logic.store_CoordInList(self.x, self.y, self.z, segmentationNode)
    #self.table = vtk.vtkColorTable()
    #self.table.DeepCopy(self.segmentationNode.GetColor().GetColorTable())
    #table = self.ColorTable.nodeTypes.GetColorTable()
    #self.ColorTable.GetColor()

  def onApplyButton(self):
    logic = visuThreeDLogic()
    #enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    #imageThreshold = self.imageThresholdSliderWidget.value
    # logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)
    #logic.store_CoordInList(self.x,self.y,self.z)
    #self.logic.ThreeD_View()
    logic.run()

  def onSearch(self, value):
    # global visuHText
    #visuHText = QLabel(self.tr("..."))
    #visuText.text(repr(value))
    print(value)
    # visuHText = self.regionSearchBox.text(str(value))
    # print visuHText
    # logic = visuThreeDLogic()
    self.logic.filterVisuHierarchyMap(value)
    # for i in self.regions:
    #     self.regionsButtonGroup.removeButton(1)

    # seartchRegionList = searchRegion.split()
    # for idx, j in enumerate(self.regions):
    #     print type(self.regions)
    #     rname = j["name"].lower()
    #     print (type(rname))
    #     if reduce(lambda x,y: x and (rname.find(y.lower())!=-1), [True] + searchRegionList):
    #         self.regions.addItem(j["name"], idx)


  def onFileLoad(self):
    
    #path = self.inputJson.getFileName(None, "File", "", "JSON File (*.json)")
    #directory = os.path.dirname(path)
    #basename = os.path.basename(path)
    #self.inputJson.addCurrentPathToHistory()
    logic = visuThreeDLogic()
    logic.readCoord_JsonFile(coord)
    #self.fileButton.enabled = self.inputJson

  def onSelectAllRegionsButton(self):
    regionButtons = self.regionsButtonGroup.buttons()
    for regionButton in regionButtons:
        regionButton.checked = True

  def onSelectNoRegionsButton(self):
    regionButtons = self.regionsButtonGroup.buttons()
    for regionButton in regionButtons:
        regionButton.checked = False
 
  def onRegionSelect(self, checkbox):
    
    print(checkbox)
    global text 
    logic = visuThreeDLogic()
    #regionButtons = self.regionsButtonGroup.buttons()
    checkedButtonId = self.regionsButtonGroup.checkedId()

    for r in range(0,len(self.regions)):

        if checkedButtonId == r:

            text = self.regions[r]
            print ('the checked region is :', text)
            logic.run()

        # # if no checkbox is checked, checkedId returns -1
        # else:

        #     text = ""
        #     print('No region is selected')
    #logic.run()
    print (checkedButtonId)
    print ('the checked region is', text)
    return text



    # for r in range(len(self.regions)):
    #     # buttonChecked = self.regionsButtonGroup.buttonClicked(r)
    #     # print buttonChecked
    #     if checkedButton == True:
    #         text = 'seed.left.frontal'
    #         logic.run
    # print (regionButtons.buttons(1))
    # for button in regionButtons:
    #     if regionButtons[1].checked == True:
    #         text = 'seed.left.frontal'
    #         logic.run
        # if regionButtons['seed left frontal'].isChecked():
        #     text = 'seed.left.frontal'
        #     logic.run
        # else:
        #     print ('not the correct checkBox')
        # if (self.regionButtons[r].isChecked()):
        #     text = 'seed.left.frontal'
        #     logic.run()
    
    # elif self.regionButtons['seed right frontal'].isChecked():
    #   text = 'seed.right.frontal'
    #   logic.run()

    # elif self.regionButtons['seed left occipital'].isChecked():
    #   text = 'seed.left.occipital'
    #   logic.run()

    # elif self.regionButtons['seed right occipital'].isChecked():
    #   text = 'seed.right.occipital'
    #   logic.run()

    # elif self.regionButtons['seed left parietal'].isChecked():
    #   text = 'seed.left.parietal'
    #   logic.run()
    # else:
    #   logic.run()

    #segmentationDisplayNode.SetSegmentVisibility(threeDNodeId, False)
    #return text

  #text = onRegionSelect(text)

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
    self.resNameRegion = []
    self.x = []
    self.y = []
    self.z = []
    self.segmentationNode = slicer.vtkMRMLSegmentationNode()
    self.index = []
    self.position = []
    self.visu = []
    # self.text = raw_input("Enter region name to visualize: ")
    #self.text = ''
    #widget = visuThreeDWidget()
    #self.text = widget.
    #self.text = 'seed.left.frontal.'
    #self.text = visuThreeDWidget.text 
    self.path_to_json ='/work/wprummel/Tools/Test-files/Connectome_3D_Visualization/nodeGraph_3D.json'
    self.user_file = '/work/maria5/EBDS_CIVILITY/DataShare/TestMatricesForVisualization/AAL78/PerNodeMetrics/Conte_EigenVectorCentrality_4Yr_AAL78Regions.csv'
    self.user_csvFile = open(self.user_file, "r")
    #self.path_to_json2 ='/work/wprummel/Tools/Test-files/Connectome_3D_Visualization/nodeGraph3D_properties.json'
    #json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    #print(json_files) 

    #d3 = self.readName_JsonFile()
    # # print(d3)
    #print(json.dumps(d3, sort_keys=True, indent=4))

    #Open json file just once and not multiple times
    self.nodeGraphArray = []
    with open(self.path_to_json, "r") as dct:
        self.nodeGraphArray = json.load(dct)

    #Open json file just once and not multiple times
    
    #d3 = self.createMatrixRowMap(self.nodeGraphArray)
    # d3 = self.CreateNodeDegreeMap(self.nodeDegreeArray)
    # print(json.dumps(d3, sort_keys=True, indent=4))
    #d5 = self.readName_JsonFile(self.nodeGraphArray)
    #print(json.dumps(d5, sort_keys=True, indent=4))

    # call function create MatrixRowMap 
    # indexes the json file by Matrix Row
    self.matrixRowMap = self.createMatrixRowMap(self.nodeGraphArray)

    # call function create VisuHierarchyMap 
    # indexes the json file by VisuHierarchy
    self.visuHierarchyMap = self.createVisuHierarchyMap(self.nodeGraphArray)
    self.visuHierarchyMapMatches = []

    #print(json.dumps(self.visuHierarchyMap, sort_keys=True, indent=4))

    # Initialize an empty filtered VisuHierarchy Map  
    self.filteredVisuHierarchy = {}

    # Map that is shown every time one of the 2 boxes (index by matrixRow or by VisuHierarchy)
    # is checked
    node = 'enter node'
    self.nodeGraphFilteredArray = {"nameN": {
        "node": node, #shows the entire node (1 section in json file)
        "visible": True #shown by default
    }}

    self.user_file = '/work/maria5/EBDS_CIVILITY/DataShare/TestMatricesForVisualization/AAL78/PerNodeMetrics/Conte_EigenVectorCentrality_4Yr_AAL78Regions.csv'

    #self.nodeGraphArray = []



    #self.user_csvFile = open(self.user_file, "r")

    self.read_csvFile(self.user_csvFile)

    self.write_json()

    #def read_csvFile(self, user_csvFile):
  def read_csvFile(self, user_csvFile):

    with self.user_csvFile as table:

        self.user_csvFile = open(self.user_file, "r")
 
        self.eigenVectCenter = csv.reader(table, delimiter=',')
        #line_count = 2
        i=2
        subject = []
        j=1

        for j in self.eigenVectCenter:

            #subject.append({", ".join(j)})
            subject.append(j)

            #subject.append(self.eigenVectCenter[2][j])
        #for row in self.eigenVectCenter:

        # if line_count == 2:

        #     print({", ".join(row)})
                #line_count += 1
            
            # else:

            #     print( {row[2]})
            #     line_count += 1
    subjectCurrent = subject[1]

    del subjectCurrent[0]
    del subjectCurrent[0]
    print subjectCurrent[1]
    print ('Current subject is :', len(subjectCurrent))
    print len(subjectCurrent)
    #print (len(subject[1]))
    return subjectCurrent
  
  def write_json(self):

    node_properties = []
    #node_properties = {}

    #node_properties['MatrixRow'] = [self.get_node_index(self.nodeGraphArray)]
    #matrixIndex = self.get_node_index(self.nodeGraphArray)
    #matrixIndex.remove(-1)

    eigenVect = self.read_csvFile(self.user_csvFile)

    for index,eigen in enumerate(eigenVect, start =1):

        node_properties.append({'MatrixRow' : index , 'properties' : {'scalars' : {'eigenVectCenter' : eigen}}})

    print (node_properties) 
    #return node_properties

    # convert node_properties [list] to dictionary 
    #it = iter(node_properties)
    #dict_prop = dict(zip(it,it)) 

    # convert into json
    json_prop = json.dumps(node_properties, sort_keys=True, indent=4)
    print (json_prop)

    # write json data to file
    with open('extract_node_properties.json', 'w') as f:
        json.dump(node_properties,f)


    # Call filter function
    # d5=self.filterVisuHierarchyMap(self.nodeGraphArray)
    # print(json.dumps(d5, sort_keys=True, indent=4))

  def get_node_index(self, nodeGraphArray):
    
    nodeIndex = []
    d_row = self.createMatrixRowMap(self.nodeGraphArray)   
    #key = "MatrixRow"  

    for key in d_row.keys():

        nodeIndex.append(key) 

    return nodeIndex

  # Map that indexes the json file by Matrix Row
  def createMatrixRowMap(self, nodeGraphArray):
    # with open(self.path_to_json, "r") as dct:
    #with open(path, "r") as json_file:
      #Stores the json data in a dictionnary
      #data = json.load(json_file)
      #data = dct.read()
      # k = json.load(dct)      
      d2 = {}      
      # for i, in range(len(k)):

      # i is the index, node is the element
      for i,node in enumerate(nodeGraphArray):
        #order dictionnary by Matrix Row
        d2[node["MatrixRow"]] = node        

      # Iterates on the reordered dictionnary d2  
      # for j in range(1,len(d2)):
      #   #d2[j].get('coord')
      #   #d2.update()
      #   coord.append(list(d2[j].get('coord')))
      #   j+=1
      return d2#coord

  # Map that indexes the json file by visuHierarchy name
  def createVisuHierarchyMap(self, nodeGraphArray):
    # with open(self.path_to_json, "r") as dct:
    #with open(path, "r") as json_file:
      #Stores the json data in a dictionnary
      #data = json.load(json_file)
      #data = dct.read()
      # k = json.load(dct)      
      d3 = {}      
      # for i, in range(len(k)):

      # i is the index, node is the element
      for i,node in enumerate(nodeGraphArray):
        #order dictionnary by Matrix Row
        if(node["VisuHierarchy"] not in d3):
            d3[node["VisuHierarchy"]] = []
        d3[node["VisuHierarchy"]].append(node)        

      return d3#coord

  # filter function linked to the search text for visuHierarchy checkbox
  def filterVisuHierarchyMap(self, search_text):

    if(search_text is not None):
        self.visuHierarchyMapMatches = []
        print(search_text)
        for key in self.visuHierarchyMap:
            regex = ".*" + search_text + ".*"
            if(len(re.findall(regex, key)) > 0):
                self.visuHierarchyMapMatches.append(key)


        print(self.visuHierarchyMapMatches)

  def CreateNodeDegreeMap(self, nodeDegreeArray):

    row = {}     
    node_degree = []
    value1 = {}
    value2 = {}

    for i,node in enumerate(self.nodeDegreeArray):

        row[node["MatrixRow"]] = node  

    value1 = row['properties']
    value2 = value1['scalars']
    node_degree = value2['node_degree'] 


    # for key, value in row.items():

    #     node_degree.append(value)
    #     print (node_degree)
  

    # for i,node in enumerate(nodeDegreeArray):
    #     #order dictionnary by Matrix Row
    #     if(node["Scalars"] not in node_degree):
    #         node_degree[node["Scalars"]] = []
    #     node_degree[node["Scalars"]].append(node)          

    return node_degree

    # self.filteredVisuHier = {}
    # visuDict = self.createVisuHierarchyMap(self.nodeGraphArray)
    # #print visuDict
    # #visuHText = 'seed.left.frontal'
    # for visuHText in visuDict.keys():
    # #for node in nodeGraphArray:
    #     #f(visuHText in visuDict.keys()): # this is the regex
    #     #if re.findall(node,visuHText):
    #     self.filteredVisuHier = visuDict.get(visuHText, None)
    #         #self.filteredVisuHier.add()
    #         #self.filteredVisuHier[node["name"]] = node
    #         #print self.filteredVisuHier
    # return self.filteredVisuHier

  # V1 Read Region Names in json file
  # def readName_JsonFile(self, nodeGraphArray):
  #   matrixDict = self.createMatrixRowMap(self.nodeGraphArray)
  #   #print (json.dumps(matrixDict, sort_keys=True, indent=4))
  #   nameRegion = []

  #   for name in matrixDict:

  #       nameRegion.append((matrixDict[name].get('VisuHierarchy')))
  #       regions = []
  #       for name in nameRegion:
  #           if name not in regions:
  #               regions.append(name)
    #print self.filteredVisuHier
    #return self.filteredVisuHier
  # V2 Read Region Names in json file
  def readName_JsonFile(self, nodeGraphArray):
    visuDict = self.createVisuHierarchyMap(self.nodeGraphArray)
    #print (json.dumps(matrixDict, sort_keys=True, indent=4))
    nameRegion = []
    for key in visuDict.keys():

        nameRegion.append(key)
        # regions = []
        # for name in nameRegion:
        #     if name not in regions:
        #         regions.append(name)
    print ('THIS: ' ,nameRegion)
    return nameRegion #regions

  #Read Region Coords in json file
  def readCoord_JsonFile(self, nodeGraphArray):
    matrixDict = self.createMatrixRowMap(self.nodeGraphArray)
    #print (json.dumps(matrixDict, sort_keys=True, indent=4))
    coordRegion = []

    for coord in matrixDict:

        coordRegion.append((matrixDict[coord].get('coord')))

    return coordRegion

    # # with open(self.path_to_json, "r") as dct:
    # #     nodeGraph = json.load(dct)
    #     d3 = {}
    #     nameRegion = []
    #     for ng in nodeGraph:
    #     #order dictionnary by Matrix Row
    #         d3[ng["MatrixRow"]] = ng

    # # Iterates on the reordered dictionnary d3
    # # Returns a list with region names in the right order
    #     d4 = {}
    #     d5 = {}
    #     for ng in nodeGraph:

    #         if ng["VisuHierarchy"] not in d4:
    #             d4[ng["VisuHierarchy"]] = []

    #         d4[ng["VisuHierarchy"]].append(ng)
    #         print (json.dumps(d4,sort_keys=True, indent=4))
    #         #print d4
    #         #nameRegion.append(list(d5[ng].get('VisuHierarchy')))
    #         #ng+=1
        
    #     for j in range(1,len(d4)):
    #     #d2[j].get('coord')
    #     #d2.update()
    #         nameRegion.append(list(d4[j].get('VisuHierarchy')))
    #     #d5=d4[self.text]
    #     #nameRegion = d5["VisuHierarchy"]
    #     #for rn in range(1,len(d4)):

    #         #d4[rn].get('VisuHierarchy')
    #         #d4.update()
    #         #nameRegion.append(list(d4[ng].get('coord')))
    #         #ng+=1


    #   #self.data = json_file.read()
    #   #self.coord = json.loads(d2, object_hook=self.decode_coord)
    #   #self.newfile = json_file.copy()
    # return nameRegion

  # def getRegionName(self):
  #   d5 = []
  #   d4 = self.readName_JsonFile()
  #   print d4["VisuHierarchy"]
  #   #d4[1].get('VisuHierarchy')
  #   #d5 = d4[]
  #   for rn in range(1,len(d4)):
  #       # if rn["VisuHierarchy"] not in d5:
  #       #     d5[rn["VisuHierarchy"]] = []
  #       #d5[rn["VisuHierarchy"]].append(rn)
  #       #d5[rn["VisuHierarchy"]]
  #       #d4[rn].get('VisuHierarchy')
  #       #d4.update()
  #       d5.append(list(d4[rn].get('VisuHierarchy')))
  #       #rn+=1
  #       print d5
  #   return d5

  
  #Store x,y,z coordinates in separate lists 
  # def store_CoordInList(self,x, y, z):
  #   coord = self.read_JsonFile(self.coord)
  #   #text = 'seed.right.frontal.'
  #   visu = []
    #position = []
    #index = []
  def patternInVisualHierarchy(self):
    region = []
    position = []
    regionList = []
    #regionList = self.readName_JsonFile(self.nodeGraphArray)
    matrixDict = self.createMatrixRowMap(self.nodeGraphArray)

    for name in matrixDict:

        region.append((matrixDict[name].get('VisuHierarchy')))
    #for i in range(len(regionList)):
    for i in range(len(region)):

        # change each element type in regionList, from unicode to string 
        regionList.append(region[i].encode('utf-8'))
    print (regionList)

    for pattern in regionList:
      if re.findall(pattern,text):
        print (text)
        position.append(1)
        print ('found match!')
      else:
        position.append(0)
        print('no match')
    #print position
    return position


  #   #liste = self.read_RegionJsonFile(self.liste)
  #   i = 0
  #   for i in range(len(self.liste)):
  # # change each element type in liste, from unicode to string 
  #     visu.append(self.liste[i].encode('utf-8'))
  #   print (visu)
  #   for pattern in visu:
  #     if re.findall(pattern, self.text):
  #     #index = visu.index('seed.right.frontal.')
  #       position.append(1)
  #       print ('found match!')
  #     else:
  #       position.append(0)
  #       print('no match')
  #   print position
  #   return position

  def getIndex(self, index):
    position = self.patternInVisualHierarchy()
    index = []
    print len(position)
    for i, e in enumerate(position):
      if e == 1:
        index.append(i)   
    print len(index)
    print index
    return index

  def store_CoordInList(self,x, y, z, segmentationNode ):
    coord = self.readCoord_JsonFile(self.nodeGraphArray)
    #print coord
    index = self.getIndex(self.index)
    print index
    print len(index)
    x = []
    y = []
    z = []
    new_coord = []
    ##### Dict
    # d2 = {}
    # d2[dct[0]["name"]] = dct[0]
    slicer.mrmlScene.AddNode(self.segmentationNode)
    stringArray = vtk.vtkStringArray()
    #self.segmentationNode.GetSegmentIDs(stringArray)
    segmentationNode.CreateDefaultDisplayNodes()
    append=vtk.vtkAppendPolyData()
    #colorVector = vtk.vtkVector3d()
    # create a sub-node that contains all the display data by using GetDisplayNode()
    segmentationDisplayNode = self.segmentationNode.GetDisplayNode()

    for j in range(len(index)):

        # color = (100, 150, 200)
        # color = np.array(color, float) / 255
        # try:
        #     segmentationNode.SetColor(color)
        # except AttributeError:  # older versions of Slicer
        #     colorVector.Set(*color)
        #     segmentationDisplayNode.SetColor(colorVector)
      #string.append(self.index[j].encode('utf-8'))
    #list_index.append(position.index(j))
    #value = list_index[j]
  #for value in (list_index):
  # if a in visu_h :
  #   a_index = np.where(np_visu_h==a)
  #   print a_index
        x.append(coord[index[j]][0])
        y.append(coord[index[j]][1])
        z.append(coord[index[j]][2])
        new_coord.append([x[j],y[j],z[j]])
        # for i in range(len(self.coord)):
        #   x = self.x.append(self.coord[i][0])
        #   y = self.y.append(self.coord[i][1])
        #   z = self.z.append(self.coord[i][2])
        threeDNode = vtk.vtkSphereSource()
        threeDNode.SetCenter(new_coord[j])
        threeDNode.SetRadius(7)
        threeDNode.Update()
        append.AddInputData(threeDNode.GetOutput())
    #print coord
    append.Update()
    threeDNodeId = self.segmentationNode.AddSegmentFromClosedSurfaceRepresentation(append.GetOutput(), "Node", colorMap)#"Node",[0.0,1.0,1.0])
    
    #triangles = vtk.vtkTriangleFilter()
    #triangles.SetInputConnection(segmentationDisplayNode.GetOutputPolyData())
    #plyWriter = vtk.vtkPLYWriter()
    #plyWriter.SetInputConnection(triangles.GetOutputPort())
    #lut = vtk.vtkColorTable()
    #lut.DeepCopy(segmentationDisplayNode.GetColor())
    #lut.SetRange(segmentationDisplayNode.GetScalarRange())
    #plyWriter.SetColorTable(lut)
    #plyWriter.SetArrayName(segmentationDisplayNode.GetActiveScalarName())
    #plyWriter.GetColors()

    #segmentationDisplayNode = self.segmentationNode.GetDisplayNode()
    segmentationDisplayNode.SetSegmentVisibility(threeDNodeId, True)
    print ('the new coord are : ', new_coord)
    return new_coord

    # Plot all connectomes
  def storeAll_CoordInList(self,x, y, z, segmentationNode ):
    coord = self.readCoord_JsonFile(self.nodeGraphArray)
    #print coord
    #index = self.getIndex(self.index)
    #print index
    #print len(index)
    #x = []
    #y = []
    #z = []
    new_coord = []
    ##### Dict
    # d2 = {}
    # d2[dct[0]["name"]] = dct[0]
    slicer.mrmlScene.AddNode(self.segmentationNode)
    #stringArray = vtk.vtkStringArray()
    #self.segmentationNode.GetSegmentIDs(stringArray)
    segmentationNode.CreateDefaultDisplayNodes()
    append=vtk.vtkAppendPolyData()
    #colorVector = vtk.vtkVector3d()
    # create a sub-node that contains all the display data by using GetDisplayNode()
    segmentationDisplayNode = self.segmentationNode.GetDisplayNode()

    for j in range(len(coord)):

        # color = (100, 150, 200)
        # color = np.array(color, float) / 255
        # try:
        #     segmentationNode.SetColor(color)
        # except AttributeError:  # older versions of Slicer
        #     colorVector.Set(*color)
        #     segmentationDisplayNode.SetColor(colorVector)
      #string.append(self.index[j].encode('utf-8'))
    #list_index.append(position.index(j))
    #value = list_index[j]
  #for value in (list_index):
  # if a in visu_h :
  #   a_index = np.where(np_visu_h==a)
  #   print a_index
        x.append(coord[j][0])
        y.append(coord[j][1])
        z.append(coord[j][2])
        new_coord.append([x[j],y[j],z[j]])
        # for i in range(len(self.coord)):
        #   x = self.x.append(self.coord[i][0])
        #   y = self.y.append(self.coord[i][1])
        #   z = self.z.append(self.coord[i][2])
        threeDNode = vtk.vtkSphereSource()
        threeDNode.SetCenter(new_coord[j])
        threeDNode.SetRadius(7)
        threeDNode.Update()
        append.AddInputData(threeDNode.GetOutput())
    #print coord
    append.Update()
    threeDNodeId = self.segmentationNode.AddSegmentFromClosedSurfaceRepresentation(append.GetOutput(), "Node", colorMap)#"Node",[0.0,1.0,1.0])
    
    #triangles = vtk.vtkTriangleFilter()
    #triangles.SetInputConnection(segmentationDisplayNode.GetOutputPolyData())
    #plyWriter = vtk.vtkPLYWriter()
    #plyWriter.SetInputConnection(triangles.GetOutputPort())
    #lut = vtk.vtkColorTable()
    #lut.DeepCopy(segmentationDisplayNode.GetColor())
    #lut.SetRange(segmentationDisplayNode.GetScalarRange())
    #plyWriter.SetColorTable(lut)
    #plyWriter.SetArrayName(segmentationDisplayNode.GetActiveScalarName())
    #plyWriter.GetColors()

    #segmentationDisplayNode = self.segmentationNode.GetDisplayNode()
    segmentationDisplayNode.SetSegmentVisibility(threeDNodeId, True)
    print ('the new coord are : ', new_coord)
    return new_coord



  def createColorMap(self):

    #self.segmentationNode.SetAndObserveColorNodeID('vkMRMLColorTableNodeRainbow')
   
    colorMap = slicer.vtkMRMLColorTableNode()
    colorMap.SetTypeToUser()
    colorMap.SetNumberOfColors(256)
    colorMap.SetName("Color Map")
    for i in range(0,255):

        colorMap.SetColor(i, 0.0, 1 - (i+1e-16)/255.0, 1.0, 1.0)

    slicer.mrmlScene.AddNode(colorMap)



  #   #imposer une autre couleur
  #   stringArray = vtk.vtkStringArray()
  #   #self.segmentationNode.GetSegmentIDs(stringArray)
  #   segmentationNode.CreateDefaultDisplayNodes()
  #   append=vtk.vtkAppendPolyData()
  #   colorVector = vtk.vtkVector3d()

  #   for j in range(len(index)):

  #       color = (100, 150, 200)
  #       color = np.array(color, float) / 255
  #       try:
  #           segmentationNode.SetColor(color)
  #       except AttributeError:  # older versions of Slicer
  #           colorVector.Set(*color)
  #           segmentationDisplayNode.SetColor(colorVector)
  #     #string.append(self.index[j].encode('utf-8'))
  #   #list_index.append(position.index(j))
  #   #value = list_index[j]
  # #for value in (list_index):
  # # if a in visu_h :
  # #   a_index = np.where(np_visu_h==a)
  # #   print a_index
  #       x.append(coord[index[j]][0])
  #       y.append(coord[index[j]][1])
  #       z.append(coord[index[j]][2])
  #       new_coord.append([x[j],y[j],z[j]])
  #       # for i in range(len(self.coord)):
  #       #   x = self.x.append(self.coord[i][0])
  #       #   y = self.y.append(self.coord[i][1])
  #       #   z = self.z.append(self.coord[i][2])
  #       threeDNode = vtk.vtkSphereSource()
  #       threeDNode.SetCenter(new_coord[j])
  #       threeDNode.SetRadius(7)
  #       threeDNode.Update()
  #       append.AddInputData(threeDNode.GetOutput())
  #   #print coord
  #   #print coord
  #   append.Update()
  #   threeDNodeId = self.segmentationNode.AddSegmentFromClosedSurfaceRepresentation(append.GetOutput(), "Node", colorVector)#, "Node",[0.0,1.0,1.0])
  #   #segmentationDisplayNode = self.segmentationNode.GetDisplayNode()
  #   segmentationDisplayNode.SetSegmentVisibility(threeDNodeId, True)
  #   print ('the new coord are : ', new_coord)
  #   return new_coord

  def run(self):
    #self.patternInVisualHierarchy(self.position)
    self.store_CoordInList(self.x,self.y,self.z, self.segmentationNode)
    #self.ThreeD_View(self.segmentationNode)
  def run_all(self):
    self.storeAll_CoordInList(self.x,self.y,self.z, self.segmentationNode)

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
    One of the most important regions of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a region that you depend on,
    your test should break so they know that the region is needed.
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
