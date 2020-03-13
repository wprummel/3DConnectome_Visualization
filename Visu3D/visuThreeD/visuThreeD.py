import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import json, ast
import re
import vtkSegmentationCorePython
import numpy as np
import json_extract_properties as JEP
import csv

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
    # self.searchBox.connect("textChanged(QString)", self.on_search)

    # # file selector
    # self.fileSelector = qt.QComboBox()
    # fileFormLayout.addRow("Filter:", self.fileSelector)

    # # add all the files listed in the json files
    # for idx,j in enumerate(self.jsonFilters):
    #   name = j["name"]
    #   self.fileSelector.addItem(name, idx)

    # # connections
    # self.fileSelector.connect('currentIndexChanged(int)', self.onFileSelect)
    #self.region_checkbox()
    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input table selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLTableNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the csv file input to the algorithm." )
    parametersFormLayout.addRow("Input Table: ", self.inputSelector)

    #
    # output volume selector
    #
    # self.outputSelector = slicer.qMRMLNodeComboBox()
    # self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    # self.outputSelector.selectNodeUponCreation = True
    # self.outputSelector.addEnabled = True
    # self.outputSelector.removeEnabled = True
    # self.outputSelector.noneEnabled = True
    # self.outputSelector.showHidden = False
    # self.outputSelector.showChildNodeTypes = False
    # self.outputSelector.setMRMLScene( slicer.mrmlScene )
    # self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    # parametersFormLayout.addRow("Output Volume: ", self.outputSelector)
    
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

    #
    # Checkbox to weather or not the input table has a header
    #
    self.headerCheckBox = qt.QCheckBox()
    self.headerCheckBox.checked = 0
    self.headerCheckBox.setToolTip("If checked, it means that the input table contains a header.")
    parametersFormLayout.addRow("Header", self.headerCheckBox)

    #
    # Table start column spinBox
    #
    self.min_column = 1.00
    self.tableStartSpinBox = qt.QDoubleSpinBox()
    self.tableStartSpinBox.singleStep = 1
    self.tableStartSpinBox.setValue(self.min_column)
    self.tableStartSpinBox.setToolTip("Set start column, this should be a value (float/int)")
    parametersFormLayout.addRow("Start Column:", self.tableStartSpinBox)

    #
    # Check box to trigger taking screen shots for later use in tutorials
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
    # Import json and csv file Area
    #
    self.fileCollapsibleButton = ctk.ctkCollapsibleButton()
    self.fileCollapsibleButton.text = "Import json or csv file"
    self.layout.addWidget(self.fileCollapsibleButton)
    self.fileImportFormLayout = qt.QFormLayout(self.fileCollapsibleButton)

    self.fileImport = ctk.ctkPathLineEdit()
    self.fileImport.filters = ctk.ctkPathLineEdit.Files
    self.fileImport.settingKey = 'JsonInputFile'
    self.fileImportFormLayout.addRow("Input Json File:", self.fileImport)
    self.path = self.fileImport.currentPath

    self.fileExport = ctk.ctkPathLineEdit()
    self.fileExport.filters = ctk.ctkPathLineEdit.Dirs
    self.fileExport.settingKey = 'JsonOutputDirs'
    self.fileImportFormLayout.addRow("Output directory:", self.fileExport)

    self.fileImportButton = qt.QPushButton('Load files')
    self.fileImportButton.checked = False
    self.fileImportFormLayout.addRow(self.fileImportButton)

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

    #
    # Threshold node value
    #
    # default values
    self.logic = visuThreeDLogic()
    self.minVal = 0.0
    self.maxVal = 0.6
    self.nodeThresholdSliderWidget = ctk.ctkRangeWidget()
    self.nodeThresholdSliderWidget.singleStep = 0.01
    self.nodeThresholdSliderWidget.setValues(self.minVal, self.maxVal)
    self.nodeThresholdSliderWidget.setMaximumValue(self.maxVal)
    self.nodeThresholdSliderWidget.setMinimumValue(self.minVal)
    self.nodeThresholdSliderWidget.setRange(self.minVal, self.maxVal)
    self.nodeThresholdSliderWidget.setMouseTracking(True)
    self.nodeThresholdSliderWidget.setEnabled(True)
    self.nodeThresholdSliderWidget.setToolTip("Set threshold node value for computing the node value.")
    self.regioncheckFormLayout.addRow("Plot property range:", self.nodeThresholdSliderWidget)

    #
    # Node size min spinBox
    #
    # default value for min size (l: lowest , h: highest)
    self.minSize_l = 0.0
    self.minSize_h = 7.0
    self.nodeMinSizeSpinBox = qt.QDoubleSpinBox()
    self.nodeMinSizeSpinBox.singleStep = 0.01
    self.nodeMinSizeSpinBox.setRange(self.minSize_l, self.minSize_h)
    self.nodeMinSizeSpinBox.setToolTip("Set minimum node size.")
    self.regioncheckFormLayout.addRow("Min size:", self.nodeMinSizeSpinBox)

    #
    # Node size max spinBox
    #
    # default value for max size (l: lowest , h: highest)
    self.maxSize_l = 7.0
    self.maxSize_h = 12.0
    self.nodeMaxSizeSpinBox = qt.QDoubleSpinBox()
    self.nodeMaxSizeSpinBox.singleStep = 0.01
    self.nodeMaxSizeSpinBox.setRange(self.maxSize_l, self.maxSize_h)
    self.nodeMaxSizeSpinBox.setToolTip("Set maximum node size.")
    self.regioncheckFormLayout.addRow("Max size:", self.nodeMaxSizeSpinBox)   

    #
    # Node Connections Area
    #
    self.lineCollapsibleButton = ctk.ctkCollapsibleButton()
    self.lineCollapsibleButton.text = "Connection Size and Color thresholding"
    self.layout.addWidget(self.lineCollapsibleButton)
    # Layout within the collapsible button
    self.lineconnectFormLayout = qt.QFormLayout(self.lineCollapsibleButton)

    #
    # input connection matrix selector
    #
    self.matrixConnectSelector = slicer.qMRMLNodeComboBox()
    self.matrixConnectSelector.nodeTypes = ["vtkMRMLTableNode"]
    self.matrixConnectSelector.selectNodeUponCreation = True
    self.matrixConnectSelector.addEnabled = False
    self.matrixConnectSelector.removeEnabled = False
    self.matrixConnectSelector.noneEnabled = False
    self.matrixConnectSelector.showHidden = False
    self.matrixConnectSelector.showChildNodeTypes = False
    self.matrixConnectSelector.setMRMLScene( slicer.mrmlScene )
    self.matrixConnectSelector.setToolTip( "Pick the connection matrix input to the algorithm." )
    self.lineconnectFormLayout.addRow("Input Connection Table: ", self.matrixConnectSelector)

    self.connectionColorTable = slicer.qMRMLColorTableComboBox()
    self.connectionColorTable.nodeTypes = ["vtkMRMLColorTableNode"]
    self.connectionColorTable.addEnabled = True
    self.connectionColorTable.removeEnabled = True
    self.connectionColorTable.noneEnabled = True
    self.connectionColorTable.showHidden = True
    self.connectionColorTable.setMRMLScene( slicer.mrmlScene )
    self.lineconnectFormLayout.addRow("Input color map: ", self.connectionColorTable)

    #
    # Threshold node connection strength
    #
    # default values
    self.logic = visuThreeDLogic()
    self.min_strength = 0.0
    self.max_strength = 0.6
    self.connectionThresholdSliderWidget = ctk.ctkRangeWidget()
    self.connectionThresholdSliderWidget.singleStep = 0.01
    self.connectionThresholdSliderWidget.setValues(self.min_strength, self.max_strength)
    self.connectionThresholdSliderWidget.setMaximumValue(self.max_strength)
    self.connectionThresholdSliderWidget.setMinimumValue(self.min_strength)
    self.connectionThresholdSliderWidget.setRange(self.minVal, self.max_strength)
    self.connectionThresholdSliderWidget.setMouseTracking(True)
    self.connectionThresholdSliderWidget.setEnabled(True)
    self.connectionThresholdSliderWidget.setToolTip("Set threshold node value for computing the node value.")
    self.lineconnectFormLayout.addRow("Plot strength range:", self.connectionThresholdSliderWidget)

    #
    # Connection min strength spinBox
    #
    # default value for min strength (l: lowest , h: highest)
    self.minStrength_l = 0.0
    self.minStrength_h = 7.0
    self.minConnectionSpinBox = qt.QDoubleSpinBox()
    self.minConnectionSpinBox.singleStep = 0.01
    self.minConnectionSpinBox.setRange(self.minStrength_l, self.minStrength_h)
    self.minConnectionSpinBox.setToolTip("Set minimum node size.")
    self.lineconnectFormLayout.addRow("Min size:", self.minConnectionSpinBox)

    #
    # Node size max spinBox
    #
    # default value for max size (l: lowest , h: highest)
    self.maxStrength_l = 7.0
    self.maxStrength_h = 12.0
    self.maxConnectionSpinBox = qt.QDoubleSpinBox()
    self.maxConnectionSpinBox.singleStep = 0.01
    self.maxConnectionSpinBox.setRange(self.maxStrength_l, self.maxStrength_h)
    self.maxConnectionSpinBox.setToolTip("Set maximum node size.")
    self.lineconnectFormLayout.addRow("Max size:", self.maxConnectionSpinBox) 

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
    #self.nodeButton.connect('mouseclick(bool)', self.onMouseClick)
    #self.applyButton.connect('clicked(bool)', self.logic.store_CoordInList(self.x,self.y,self.z))
    #self.applyButton.connect('clicked(bool)', self.on_apply_button)  
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.on_select)
    #self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.on_select)
    #self.regionsButtonGroup.connect('clicked()', self.region_checkbox())
    self.regionsButtonGroup.buttonClicked.connect(self.on_region_select)
    #self.calculateAllregionsButton.connect(self.on_select_all_regionsButton)
    self.regionsButtonGroup.buttonReleased.connect(self.cleanup)
    #singal is TextChanged
    self.regionSearchBox.connect("textChanged(QString)", self.on_search)
    #self.fileImportButton.connect('clicked(bool)', self.on_browse)
    self.fileImportButton.connect('clicked(bool)', self.on_file_load)
    #self.ColorTable.connect("currentNodeChanged(vtkMRMLColorTableNode*)", "setColorNode(vtkMRMLColorTableNode*)")
    #self.ColorTable.connect("setColorNode(vtkMRMLColorTableNode*)", self.ColorTable.currentNode())

    self.ColorTable.connect("currentNodeChanged(vtkMRMLNode*)", self.on_node_color_clicked)
    self.nodeThresholdSliderWidget.connect("valuesChanged(double, double)", self.sliderbar_changed)
    self.nodeMinSizeSpinBox.connect("valueChanged(double)", self.min_size_changed)
    self.nodeMaxSizeSpinBox.connect("valueChanged(double)", self.max_size_changed)
    self.tableStartSpinBox.connect("valueChanged(double)", self.table_start_changed)
    self.matrixConnectSelector.connect("currentNodeChanged(vtkMRMLNode*)",self.on_select_matrix)
    self.connectionThresholdSliderWidget.connect("valuesChanged(double, double)", self.sliderbar_changed)
    self.connectionColorTable.connect("currentNodeChanged(vtkMRMLNode*)", self.on_connect_color_clicked)
    # self.nodeThresholdSliderWidget.connect('sliderReleased(double,double)', self.SliderBar)
    #self.ColorTable.setCurrentNodeID("vtkMRMLColorTableNode *")
    
    # self.regionButtons = self.regionsButtonGroup.buttons()
    # for regionButton in self.regionButtons:
    #     regionButton.connect('clicked(bool)', self.region_checkbox()) #self.on_region_select(r))
    #self.regionsButtonGroup.connect('clicked(bool)', self.region_checkbox())

    #self.inputJson.connect('browse()', self.on_select)
    
    # Add vertical spacer
    self.layout.addStretch(1)
    # Refresh Apply button state
    self.applyButton.enabled = self.inputSelector.currentNode()
    #self.on_select()
    self.file_path = ""
    self.header = None

    #self.region_checkbox()

    #
    # Get the brain regions dynamically
    #
  def on_browse(self):
    try:
        self.fileImport.addCurrentPathToHistory()
        self.fileExport.addCurrentPathToHistory()
        self.statusLabel.plainText = ''
    except Exception as e:
      #self.addLog("Unexpected error: {0}".format(e.message))
      import traceback
      traceback.print_exc()

  def region_checkbox(self,r):
    for r in self.regions:
        print (" Thank you! ")
    #self.regionsButtonGroup.connect('toggled(bool)', self.on_apply_button)

  def cleanup(self):
    pass

  def on_header_select(self, header):
    if self.headerCheckBox.checked == True:
        header = True

    else:
        header = False

    self.logic.set_header_state(header)
    return header

  def on_select(self, table):
    print ('table', table)
    self.header = self.on_header_select(self.header)
    print ('header state', self.header)
    self.logic.set_header_state(self.header)
    self.logic.set_user_table(table)
    self.logic.update()

  def on_select_matrix(self, connection_matrix):
    #print ('matrix:', connection_matrix)
    self.logic.set_connection_matrix(connection_matrix)
    self.logic.update()

  def on_node_color_clicked(self, color_map):    
    #print (color_map)
    self.logic.set_node_color_map(color_map)
    self.logic.update()

  def on_connect_color_clicked(self, color_map):    
    #print (color_map)
    self.logic.set_connect_color_map(color_map)
    self.logic.update()
    
  def on_apply_button(self):
    self.logic.run_all()

  def on_search(self, value):
    print(value)
    self.logic.filter_visu_hierarchyMap(value)

  def on_file_load(self, path_to_json):
    path_to_json = self.fileImport.currentPath
    self.logic.set_input_json(path_to_json)
    self.logic.update()
    print ('The current path is:', path_to_json)
    
  def on_select_all_regionsButton(self):
    regionButtons = self.regionsButtonGroup.buttons()
    for regionButton in regionButtons:
        regionButton.checked = True

  def on_select_no_regionsButton(self):
    regionButtons = self.regionsButtonGroup.buttons()
    for regionButton in regionButtons:
        regionButton.checked = False
 
  def on_region_select(self, checkbox):
    print(checkbox)
    global text 
    # logic = visuThreeDLogic()
    #regionButtons = self.regionsButtonGroup.buttons()
    checkedButtonId = self.regionsButtonGroup.checkedId()

    for r in range(0,len(self.regions)):

        if checkedButtonId == r:

            text = self.regions[r]
            print ('the checked region is :', text)
            logic.run()

    #logic.run()
    print (checkedButtonId)
    print ('the checked region is', text)
    return text

  def sliderbar_changed(self, newMin, newMax): #node_range):
    self.logic.set_range(newMin, newMax)
    #self.logic.set_sphere_radius(self.max_size)
    self.logic.update()

  def min_size_changed(self, min_size):
    self.logic.set_min_size(min_size)
    self.logic.update()

  def max_size_changed(self, max_size):
    self.logic.set_max_size(max_size)
    # self.logic.create_node_actors()
    #self.logic.set_sphere_radius()
    self.logic.update()

  def table_start_changed(self, table_start):
    self.logic.set_table_start(table_start)
    self.logic.update()

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
    self.segmentationNode = slicer.vtkMRMLModelDisplayNode()
    self.index = []
    self.position = []
    self.visu = []
    #self.connections = []

    self.subject_index = 0
    self.min_column = 1
    self.max_column = 79

    # self.subject_index = 0
    # self.min_column = 0
    # self.max_column = 78

    #self.header = None
    # self.set_header_state(self.header)
    # if self.header == True:
    #     self.subject_index = 1
    #     self.min_column = 1
    #     self.max_column = 79
    # else:
    #     self.subject_index = 0
    #     self.min_column = 0
    #     self.max_column = 78

    # self.text = raw_input("Enter region name to visualize: ")
    #self.text = ''
    #widget = visuThreeDWidget()
    #self.text = widget.
    #self.text = 'seed.left.frontal.' 
    #self.text = visuThreeDWidget.text 

    self.path_to_json ='/work/wprummel/Tools/Test-files/Connectome_3D_Visualization/nodeGraph_3D.json'
    self.jep = JEP.json_extract_properties()
    #self.path_to_json = None
    #self.path = None
    # self.path_to_json = self.set_input_json(self.path_to_json)
    # #self.path_to_json = self.set_input_json(self.path_to_json).encode('utf-8')
    # self.node_graph_array = []
    # with open(self.path_to_json, "r") as json_file:
    #     self.node_graph_array = json.load(json_file)

    #Open json file just once and not multiple times
    
    #d3 = self.create_matrix_rowMap(self.nodeGraphArray)
    # d3 = self.create_node_degreeMap(self.nodeDegreeArray)
    # print(json.dumps(d3, sort_keys=True, indent=4))
    #d5 = self.read_name_jsonFile(self.nodeGraphArray)
    #print(json.dumps(d5, sort_keys=True, indent=4))
    #self.set_input_json(self.path_to_json)
    self.set_node_graph_array()

    # call function create MatrixRowMap 
    # indexes the json file by Matrix Row
    # self.set_node_graph_array()
    # self.matrixRowMap = self.create_matrix_rowMap(self.node_graph_array)
    self.set_matrix_row_map()

    # call function create VisuHierarchyMap 
    # indexes the json file by VisuHierarchy
    # self.visuHierarchyMap = self.create_visu_hierarchyMap(self.node_graph_array)  
    self.set_matrix_hierarchy_map()  
    #self.set_line_connection()

    #print(json.dumps(self.visuHierarchyMap, sort_keys=True, indent=4))

    # Initialize an empty filtered VisuHierarchy Map  
    self.filteredVisuHierarchy = {}

    #self.set_connection_matrix(self.connection_matrix)

    self.node_color_map = None
    self.connect_color_map = None
    self.user_table = None
    self.vtk_spheres = None
    self.header = False
    self.connection_matrix = None
    #self.listOfCoordinates = []
    self.node_size = 7
    self.min_size = 1
    self.max_size = 7
    self.node_min = 0
    self.node_max = 0.6

  def set_input_json(self, path_to_json):
    self.path_to_json = path_to_json
    #self.path = path_to_json.encode('utf-8')
    #self.path_to_json = path_to_json
    print('the path is:', path_to_json)
    #print('the path is:', self.path)
    #self.path_to_json = self.set_input_json(self.path_to_json).encode('utf-8')

  def set_node_graph_array(self):
    self.node_graph_array = []
    #path = self.set_input_json(self.path_to_json)
    #self.path = self.path_to_json.encode('utf-8')
    with open(self.path_to_json, "r") as json_file:
        self.node_graph_array = json.load(json_file)
    #self.node_graph_array = node_graph_array
    #print ('node graph array:', self.node_graph_array)

  def set_matrix_row_map(self):
    self.matrixRowMap = self.create_matrix_rowMap(self.node_graph_array)

  def set_matrix_hierarchy_map(self):
    self.visuHierarchyMap = self.create_visu_hierarchyMap(self.node_graph_array)

  def set_node_color_map(self, color_map):
    self.node_color_map = color_map

  def set_connect_color_map(self, color_map):
    self.connect_color_map = color_map

  def set_range(self,newMin, newMax):
    self.node_min = newMin
    self.node_max = newMax

  def set_user_file(self, userfile):
    self.user_file = userfile
    self.jep = JEP.json_extract_properties()
    self.jep.set_csv_file(self.user_file)
    self.jep.read_csv()
    #print(self.jep.get_subject_content(1))
    # jep.set_output_directory('/work/wprummel/data/maria5/EBDS_CIVILITY')

  def set_header_state(self, header):
    self.header = header

  # Store the values of our Table Node in an array : self.values
  def set_user_table(self, table):
    self.set_table_index()
    self.jep.set_table(table)

  def set_table_start(self, table_start):
    self.min_column = table_start

  def set_table_index(self):
    self.set_header_state(self.header)
    # if self.header == True:
    #     self.subject_index = 1
    # else:
    if self.header == False:
        #self.subject_index = 0
        self.min_column = self.set_table_start(self.min_column)
        # self.min_column = 0
        self.max_column = 78
    else:
        self.subject_index = 1
        self.min_column = 1
        self.max_column = 79
    return self.subject_index

  def set_connection_matrix(self, connection_matrix):
    #self.jep.set_table(connection_matrix)
    #self.connect = self.jep.set_matrix_connections(connection_matrix)
    self.jep.set_matrix_connections(connection_matrix)
    #print ('len connection list:', len(self.connections))
    #print ('connection_matrix', connection_matrix)
    #self.connections = self.jep.set_connections()
    # print ('connections:', self.connect)
    # return self.connect

  def set_minprop_value(self, minVal):
    #self.set_user_table(self.user_table)
    self.minVal = 0

  def update(self):
    self.set_table_index()
    self.set_sphere_radius(self.node_max)
    self.set_node_actors_properties()
    #self.create_line_actors()
    self.set_line_actors_properties()
    self.set_line_connection()
    self.render()

  def get_node_index(self, node_graph_array):
    
    nodeIndex = []
    d_row = self.create_matrix_rowMap(self.node_graph_array)   
    
    #key = "MatrixRow"  
    for key in d_row.keys():

        nodeIndex.append(key) 

    return nodeIndex

  # Map that indexes the json file by Matrix Row
  def create_matrix_rowMap(self, node_graph_array):
    
      d2 = {}      

      # i is the index, node is the element
      for i,node in enumerate(node_graph_array):
        #order dictionnary by Matrix Row
        d2[node["MatrixRow"]] = node        

      return d2

  # Map that indexes the json file by visuHierarchy name
  def create_visu_hierarchyMap(self, node_graph_array):
 
      d3 = {}      

      # i is the index, node is the element
      for i,node in enumerate(node_graph_array):
        #order dictionnary by Matrix Row
        if(node["VisuHierarchy"] not in d3):
            d3[node["VisuHierarchy"]] = []
        d3[node["VisuHierarchy"]].append(node)        

      return d3

  # filter function linked to the search text for visuHierarchy checkbox
  def filter_visu_hierarchyMap(self, search_text):

    if(search_text is not None):
        self.visuHierarchyMapMatches = []
        print(search_text)

        for key in self.visuHierarchyMap:
            regex = ".*" + search_text + ".*"

            if(len(re.findall(regex, key)) > 0):
                self.visuHierarchyMapMatches.append(key)

        print(self.visuHierarchyMapMatches)

# function NEVER CALLED
  def create_node_degreeMap(self, nodeDegreeArray):

    row = {}     
    node_degree = []
    value1 = {}
    value2 = {}

    for i,node in enumerate(self.nodeDegreeArray):

        row[node["MatrixRow"]] = node  

    value1 = row['properties']
    value2 = value1['scalars']
    node_degree = value2['node_degree']         

    return node_degree

# function NEVER CALLED
  def read_name_jsonFile(self, node_graph_array):
    visuDict = self.create_visu_hierarchyMap(self.node_graph_array)
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

# function NEVER CALLED
  #Read Region Coords in json file
  def read_coord_jsonFile(self, node_graph_array):
    matrixDict = self.create_matrix_rowMap(self.node_graph_array)
    #print (json.dumps(matrixDict, sort_keys=True, indent=4))
    coordRegion = []

    for coord in matrixDict:

        coordRegion.append((matrixDict[coord].get('coord')))

    return coordRegion
  
  def pattern_in_visualHierarchy(self):
    region = []
    position = []
    regionList = []
    #regionList = self.read_name_jsonFile(self.node_graph_array)
    matrixDict = self.create_matrix_rowMap(self.node_graph_array)

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

#function NEVER CALLED
  def get_index(self, index):
    position = self.pattern_in_visualHierarchy()
    index = []
    print len(position)
    for i, e in enumerate(position):
      if e == 1:
        index.append(i)   
    print len(index)
    print index
    return index

  def set_min_size(self, min_size):
    self.min_size = min_size
    print ("node min size is :", min_size)

  def set_max_size(self, max_size):
    self.max_size = max_size
    print ("node max size is :", max_size)

  def get_node_max(self, node_max):
    self.node_max = node_max
    print ("node max size is :", node_max)

  def set_node_size(self):
    self.node_size = [self.min_size, self.max_size]

  def create_node_actors(self):
    lm = slicer.app.layoutManager()
    threeDView = lm.threeDWidget(0).threeDView()
    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
    # Clear the renderer from previous actors
    # renderer.RemoveAllViewProps()
    # Generate an empty list to store each Sphere
    self.vtk_spheres = []
    
    for node in self.node_graph_array:

        if node['MatrixRow'] != -1:

            # Dictionnary of all the spheres
            sphere = {}

            sphere['source'] = vtk.vtkSphereSource()
            sphere['source'].SetCenter(node['coord'])
            sphere['source'].SetRadius(7)

            sphere['actor'] = vtk.vtkActor()
            sphere_mapper = vtk.vtkPolyDataMapper()
            
            sphere_mapper.SetInputConnection(sphere['source'].GetOutputPort())
            sphere['actor'].SetMapper(sphere_mapper)
            
            self.vtk_spheres.append(sphere)

            renderer.AddActor(sphere['actor'])

  def render(self):
    lm = slicer.app.layoutManager()
    threeDView = lm.threeDWidget(0).threeDView()
    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
    renderer.Render()

  def set_sphere_radius(self, node_max):

    value_list = self.jep.get_subject_values(self.subject_index, self.min_column, self.max_column)
    #self.value_list = self.jep.get_values()
    #self.value_list = self.set_user_table(self.user_table)
    len_sphere_actors = len(self.vtk_spheres)
    print('nbspheres:', len_sphere_actors)
    print('nbvalues:', len(value_list))

    for index in range(len_sphere_actors):

        if(index < len(value_list)):
            prop_value = (value_list[index])
            vtk_sphere = self.vtk_spheres[index]
            #len_line_actors = len(self.line_actors)
            line = self.line_actors[index]
            # a = vtk_sphere['source'].GetCenter()
            # # print('sphere center:', a , type(a))
            # b = line['source'].GetPoint1()
            # print ('center', a , 'point 1:', b)

            if (prop_value < self.node_min):  

                vtk_sphere['source'].SetRadius(self.min_size)
                vtk_sphere['actor'].SetVisibility(False)

                # if vtk_sphere['source'].GetCenter() == line['source'].GetPoint2():

                #     line['actor'].SetVisibility(False)
                #     print('true')

            elif (prop_value > self.node_max):

                vtk_sphere['source'].SetRadius(self.max_size)
                vtk_sphere['actor'].SetVisibility(True)

            else:   

                vtk_sphere['source'].SetRadius(((prop_value - self.node_min)/self.node_max)*(self.max_size - self.min_size) + self.min_size)
                vtk_sphere['actor'].SetVisibility(True)

  def set_node_actors_properties(self):
    value_list = self.jep.get_subject_values(self.subject_index, self.min_column, self.max_column)
    self.range_list = [self.node_min, self.node_max]
    if self.vtk_spheres and self.node_color_map and value_list:        

        len_sphere_actors = len(self.vtk_spheres)
        lookup_table = self.node_color_map.GetLookupTable()        
        lookup_table.SetRange(self.node_min, self.node_max)

        print('range:', lookup_table.GetRange())

        for index, sphere in enumerate(self.vtk_spheres):
            
            color = [0,0,0]

            #lookup_table.GetColor(float(self.value_list[index]),color)
            lookup_table.GetColor(value_list[index],color)
            sphere['actor'].GetProperty().SetColor(color) 

  def create_line_actors(self):

    lm = slicer.app.layoutManager()
    threeDView = lm.threeDWidget(0).threeDView()
    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()

    self.line_actors = []
    self.tube_actors = []

    # By default each connection is connected to every node
    for i, node_i in enumerate(self.node_graph_array):
        current_line_actors = []
        for j in range(i + 1, len(self.node_graph_array)):
            node_j = self.node_graph_array[j]
            self.list_index = i

            if node_i['MatrixRow'] != -1:

                # instantiate two dictionnaries
                line = {}
                tube = {}

                line['source'] = vtk.vtkLineSource()
                line['source'].SetPoint1(node_i['coord'])

                line['source'].SetPoint2(node_j['coord'])

                line['seed'] = node_i
                line['target'] = node_j

                #create mapper and actor    
                line['actor'] = vtk.vtkActor()
                line_mapper = vtk.vtkPolyDataMapper()

                line_mapper.SetInputConnection(line['source'].GetOutputPort())
                line['actor'].SetMapper(line_mapper)
                line['actor'].GetProperty().SetOpacity(0.1)

                renderer.AddActor(line['actor'])

                self.line_actors.append(line)

                # Add a tube around each line 
                tube['filter'] = vtk.vtkTubeFilter()
                tube['filter'].SetInputConnection(line['source'].GetOutputPort())
                tube['filter'].SetRadius(0.5)
                tube['filter'].SetNumberOfSides(50)

                #create mapper and actor
                tube['actor'] = vtk.vtkActor()
                tube['mapper'] = vtk.vtkPolyDataMapper()

                tube['mapper'].SetInputConnection(tube['filter'].GetOutputPort())
                tube['actor'] .GetProperty().SetOpacity(1)
                tube['actor'] .SetMapper(tube['mapper'])

                self.tube_actors.append(tube)

                renderer.AddActor(tube['actor'])

    #print ('line dictionnary:', line)

  def set_line_connection(self):

    rows = []
    positions = []
    self.listOfCoordinates = []

    # Store data in array 
    for row_index in range(len(self.jep.get_connection_rows(0))):     

        row_content = self.jep.get_connection_rows(row_index)
        position = row_content.index(0)
        rows.append(row_content)
        positions.append(position)
    row_array = np.array(rows)
    print('VAL:', len(row_array))
    # lower triangle
    lower_triangle = np.tril(row_array, -1)
    print('lower triangle:', lower_triangle)
    print ('number of rows', np.size(row_array, 0))

    # np.where returns a tuple of ndarrays
    #selection_matrix = np.where(row_array!=0, 1, 0)
    selection_matrix = np.where(row_array)
    print (selection_matrix[0], selection_matrix[1])

    len_line_actors = len(self.line_actors)
    print('nblines:', len_line_actors)


    #zip the 2 arrays to get the exact coordinates where there is no connection
    self.listOfCoordinates= list(zip(selection_matrix[0], selection_matrix[1]))
    print ('len listOfCoordinates', len(self.listOfCoordinates))

    for i in range (1,2):
        line = self.line_actors[i]
        tube = self.tube_actors[i]
        lower_triangle = []
        #iterations = (len(self.listOfCoordinates) - 1) - i
        iterations = 2
        row = i
        col = 0
        #lower_triangle = np.empty(dimension)

        while iterations > 0:

            lower_triangle.append(row_array[col][row])
            #np.append(lower_triangle, row_array[row][col], axis = 0)
            row += 1
            col += 1
            iterations -= 1
              

        if np.where(row_array == 0):
            line['actor'].SetVisibility(False)
            tube['actor'].SetVisibility(False)
        else:
            line['actor'].SetVisibility(True)
            tube['actor'].SetVisibility(True)   
    print ('lower triangle:', lower_triangle)  


    # for index in range(len(self.listOfCoordinates)):
    #     line = self.line_actors[index]
    #     tube = self.tube_actors[index]
    #     #print (self.listOfCoordinates[index]) 

    #     #for i in range(len(self.vtk_spheres)):
    #     #vtk_sphere = self.vtk_spheres[index]

    #     line['coord'] = self.listOfCoordinates[index]

    #     # If value in connection matrix is zero, then there is no connection
    #     # We set the visibility off : False
    #     if np.where(row_array == 0):
    #     #if row_array == 0:
    #         # a = line['source'].GetPoint1()
    #         # b = line['source'].GetPoint2()
    #         # print ('point 1:', a , 'point2 :', b )
    #         line['actor'].SetVisibility(False)
    #         tube['actor'].SetVisibility(False)

    #     # elif vtk_sphere['actor'].SetVisibility(False):
    #     #     line['actor'].SetVisibility(False)

    #     else:
    #         line['actor'].SetVisibility(True)
    #         tube['actor'].SetVisibility(True)

  def set_line_actors_properties(self):
    for row_index in range(len(self.jep.get_connection_rows(0))):    

        row_content = self.jep.get_connection_rows(row_index)

    if self.line_actors and self.connect_color_map: #and matrix:        

        len_line_actors = len(self.line_actors)
        lookup_table = self.connect_color_map.GetLookupTable()        
        #lookup_table.SetRange(self.node_min, self.node_max)

        #print('range:', lookup_table.GetRange())

        #for index, line in enumerate((self.listOfCoordinates)):
        for index in range(len(self.listOfCoordinates)):
            line = self.line_actors[index]
            color = [0,0,0]

            #lookup_table.GetColor(float(self.value_list[index]),color)
            lookup_table.GetColor(row_content[index], color)
            line['actor'].GetProperty().SetColor(color) 

#function NEVER CALLED
  def run_slider(self, imageThreshold):
    self.coord_value_dic()

  # def run_all(self):
  #   visu_logic = slicer.modules.visuThreeDWidget.logic
  #   visu_logic.set_user_file('/work/maria5/EBDS_CIVILITY/DataShare/TestMatricesForVisualization/AAL78/PerNodeMetrics/Conte_EigenVectorCentrality_4Yr_AAL78Regions.csv')
  #   visu_logic.create_node_actors()
  #   visu_logic.create_line_actors()
  #   visu_logic.update()

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

    visu_logic = slicer.modules.visuThreeDWidget.logic
    #visu_logic.set_user_table(self.table)
    #visu_logic.set_user_file('/work/maria5/EBDS_CIVILITY/DataShare/TestMatricesForVisualization/AAL78/PerNodeMetrics/Conte_EigenVectorCentrality_4Yr_AAL78Regions.csv')
    visu_logic.set_user_file('/home/wprummel/Documents/neo-0042-4year_AvgSym_normFull.csv')
    visu_logic.create_node_actors()
    visu_logic.create_line_actors()
    visu_logic.update()
    # visu_logic.set_node_range()

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

#     import json
#     #Access json data
#     def decode_coord(dct):
#       if "coord" in dct:
#         return (dct["coord"])
#       return dct

#     def decode_hierarchy(dct):
#       if "VisuHierarchy" in dct:
#         return (dct["VisuHierarchy"])
#       return dct

#     def decode_name(dct):
#       if "name" in dct:
#         return (dct["name"])
#       return dct

#     #read json file
#     #def read_JsonFile():
#     coord = []
#     node_tag = []
#     with open("/work/wprummel/Tools/Test-files/Connectome_3D_Visualization/nodeGraph_3D.json", "r") as json_file:
#       #Stores the json data in a dictionnary
#       # data = json.load(json_file)
#       data = json_file.read()
#       coord = json.loads(data, object_hook=decode_coord)
#       node_tag = json.loads(data, object_hook=decode_name)

# #     chart = vtk.vtkChartXYZ()
# # view = vtk.vtkContextView()
# # view.GetRenderWindow().SetSize(400,300)
# # view.GetScene().AddItem(chart)
# # chart.SetGeometry(vtk.vtkRectf(75.0,20.0,250,260))

# # table = vtk.vtkTable()
# # arrX=vtk.vtkFloatArray()
# # arrX.SetName("x")
# # table.AddColumn(arrX)
# # arrY=vtk.vtkFloatArray()
# # arrY.SetName("y")
# # table.AddColumn(arrY)
# # arrZ=vtk.vtkFloatArray()
# # arrZ.SetName("z")
# # table.AddColumn(arrZ)


#     X=10
#     Y=10
#     Z=10
#     # x = [-38.65, 41.37]
#     # y = [-5.68,-8.21]
#     # z = [50.94,52.09]
#     x = []
#     y = []
#     z = []
#     for i in range(len(coord)):
#       x.append(coord[i][0])
#       y.append(coord[i][1])
#       z.append(coord[i][2])

#     liste_x = []
#     liste_y = []
#     liste_z = []
#     for i in range(len(x)):
#       delta_x = x[i]
#       delta_y = y[i]
#       delta_z = z[i]
#       liste_x.append(delta_x)
#       liste_y.append(delta_y)
#       liste_z.append(delta_z)

# # numNodes=3
# # r=4
# # points_x=[]
# # table.SetNumberOfRows(numNodes)
# # for i in range(1):
# #   table.SetValue(i, 0, liste_x[i])
# #   table.SetValue(i, 1, liste_y[i]) 
# #   table.SetValue(i, 2, liste_z[i]) 

#     #Create Segmentation node that stores a set of segments
#     # segmentationNode = slicer.vtkMRMLSegmentationNode()
#     # slicer.mrmlScene.AddNode(segmentationNode)
#     #enable node display
#     segmentationNode.CreateDefaultDisplayNodes()
#     #if we define a master volume loaded by the user
#     # segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)

#     #Create nodes
#     #coord=[]
#     append=vtk.vtkAppendPolyData()
#     for i in range(len(liste_x)):
#       coord.append([liste_x[i], liste_y[i], liste_z[i]])
#       threeDNode = vtk.vtkSphereSource()
#       threeDNode.SetCenter(coord[i])
#       threeDNode.SetRadius(7)
#       threeDNode.Update()
#       append.AddInputData(threeDNode.GetOutput())

#     append.Update()
#     threeDNodeId = segmentationNode.AddSegmentFromClosedSurfaceRepresentation(append.GetOutput(), "Node",[0.0,1.0,1.0])

#     segmentationDisplayNode = segmentationNode.GetDisplayNode()
#     segmentationDisplayNode.SetSegmentVisibility(threeDNodeId, False)
