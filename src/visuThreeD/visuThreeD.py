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
import math

#
# visuThreeD
#

class visuThreeD(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Brain Connectome Visualization" 
    self.parent.dependencies = []
    self.parent.contributors = ["Ms. Wieke Prummel (CPE intern at NIRAL, University of North Carolina), Dr. Juan Prieto (NIRAL, University of North Carolina), Dr. Martin Styner (NIRAL, University of North Carolina)"]
    self.parent.helpText = """
This is a Brain Connectome Visualization Module. This module allows the user to visualize different regions and how they are connected. 
The User can import different data such as an eigenvectors, strength and other matrixes. 
This data will allow the user to see a variation of size and color between each connection and region. 
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """

""" # replace with organization, grant and thanks.

#
# visuThreeDWidget
#

class visuThreeDWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    ###################################
    # Import node graph json file Area
    ###################################
    self.fileCollapsibleButton = ctk.ctkCollapsibleButton()
    self.fileCollapsibleButton.text = "Import Node Graph Json File"
    self.layout.addWidget(self.fileCollapsibleButton)
    self.fileImportFormLayout = qt.QFormLayout(self.fileCollapsibleButton)

    self.fileImport = ctk.ctkPathLineEdit()
    self.fileImport.filters = ctk.ctkPathLineEdit.Files
    self.fileImport.settingKey = 'JsonInputFile'
    self.fileImport.currentPath = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), './Resources/nodeGraph_3D.json'))
    self.fileImportFormLayout.addRow("Input Json File:", self.fileImport)

    self.fileImportButton = qt.QPushButton('Load File')
    self.fileImportFormLayout.addRow(self.fileImportButton)

    ###################################
    # Node Table Area
    ###################################
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Node Table"
    self.layout.addWidget(parametersCollapsibleButton)
    # Layout within the collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Checkbox to see whether or not the input table has a header
    #
    self.headerCheckBox = qt.QCheckBox()
    self.headerCheckBox.checked = 0
    self.headerCheckBox.setToolTip("If checked, it means that the input node table contains a header.")
    parametersFormLayout.addRow("Header in Node Table", self.headerCheckBox)

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
    self.inputSelector.setToolTip( "The input file loaded trough the import Data module should be a one line table (with or without header)." )
    parametersFormLayout.addRow("Input Table: ", self.inputSelector)

    #
    # Table start column spinBox
    #
    self.min_column = 1
    self.tableStartSpinBox = qt.QDoubleSpinBox()
    self.tableStartSpinBox.singleStep = 1
    self.tableStartSpinBox.setValue(self.min_column)
    self.tableStartSpinBox.setDecimals(0)
    self.tableStartSpinBox.setToolTip("Set start column, if the first column contains a string of characters(ex: subject name) then this column should be skipped and the start column is thus 1. This should be an integer (int)")
    parametersFormLayout.addRow("Start Column:", self.tableStartSpinBox)

    ###################################
    # Region Selector Area
    ###################################
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
    self.regionSearchBox.searchIcon
    self.searchLayout.addWidget(self.regionSearchBox)

    self.logic = visuThreeDLogic()
    self.regionsLayout = qt.QHBoxLayout()
    self.nodeselectFormLayout.addRow('Regions:', self.regionsLayout)
    self.regionButtons = ctk.ctkCheckableComboBox()
    self.regionsLayout.addWidget(self.regionButtons)

    # Add buttons to select all or no region
    self.buttonsLayout = qt.QHBoxLayout()
    self.nodeselectFormLayout.addRow('Select:', self.buttonsLayout)
    self.calculateAllregionsButton = qt.QPushButton('Select All')
    self.calculateAllregionsButton.toolTip = 'Select all regions.'
    self.calculateAllregionsButton.enabled = True
    self.buttonsLayout.addWidget(self.calculateAllregionsButton)
    self.calculateAllFilteredregionsButton = qt.QPushButton('Select Filtered')
    self.calculateAllFilteredregionsButton.toolTip = 'Select all  filtered regions.'
    self.calculateAllFilteredregionsButton.enabled = True
    self.buttonsLayout.addWidget(self.calculateAllFilteredregionsButton)

    self.deselectButtonsLayout = qt.QHBoxLayout()
    self.nodeselectFormLayout.addRow('Deselect:', self.deselectButtonsLayout)
    self.calculateNoregionsButton = qt.QPushButton('Deselect All')
    self.calculateNoregionsButton.toolTip = 'Deselect all regions.'
    self.calculateNoregionsButton.enabled = True
    self.deselectButtonsLayout.addWidget(self.calculateNoregionsButton)
    self.calculateNoFilteredregionsButton = qt.QPushButton('Deselect Filtered')
    self.calculateNoFilteredregionsButton.toolTip = 'Deselect all filtered regions.'
    self.calculateNoFilteredregionsButton.enabled = True
    self.deselectButtonsLayout.addWidget(self.calculateNoFilteredregionsButton)

    ###################################
    # Node Size and colorbar thresholding Area
    ###################################
    self.colorbarCollapsibleButton = ctk.ctkCollapsibleButton()
    self.colorbarCollapsibleButton.text = "Node Size and Color Thresholding"
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
    self.regioncheckFormLayout.addRow("Input Color Map: ", self.ColorTable)

    #
    # Threshold node value
    #
    # default values
    self.minVal = 0.0
    self.maxVal = 1.0
    self.nodeThresholdSliderWidget = ctk.ctkRangeWidget()
    self.nodeThresholdSliderWidget.singleStep = 0.01
    self.nodeThresholdSliderWidget.setValues(self.minVal, self.maxVal)
    self.nodeThresholdSliderWidget.setMaximumValue(self.maxVal)
    self.nodeThresholdSliderWidget.setMinimumValue(self.minVal)
    self.nodeThresholdSliderWidget.setRange(self.minVal, self.maxVal)
    self.nodeThresholdSliderWidget.setMouseTracking(True)
    self.nodeThresholdSliderWidget.setEnabled(True)
    self.nodeThresholdSliderWidget.setToolTip("Set threshold node value for computing the node value.")
    self.regioncheckFormLayout.addRow("Plot Property Range:", self.nodeThresholdSliderWidget)

    #
    # Node size min spinBox
    #
    # default value for min size (l: lowest , h: highest)
    self.minSize_l = 0.0
    self.minSize_h = 100.0
    self.nodeMinSizeSpinBox = qt.QDoubleSpinBox()
    self.nodeMinSizeSpinBox.singleStep = 0.01
    self.nodeMinSizeSpinBox.setRange(self.minSize_l, self.minSize_h)
    self.nodeMinSizeSpinBox.setToolTip("Set minimum node size.")
    self.regioncheckFormLayout.addRow("Min Size:", self.nodeMinSizeSpinBox)

    #
    # Node size max spinBox
    #
    # default value for max size (l: lowest , h: highest)
    self.maxSize_l = 0.0
    self.maxSize_h = 100.0
    self.nodeMaxSizeSpinBox = qt.QDoubleSpinBox()
    self.nodeMaxSizeSpinBox.singleStep = 0.01
    self.nodeMaxSizeSpinBox.setRange(self.maxSize_l, self.maxSize_h)
    self.nodeMaxSizeSpinBox.setToolTip("Set maximum node size.")
    self.regioncheckFormLayout.addRow("Max Size:", self.nodeMaxSizeSpinBox)   

    ###################################
    # Connections line/tube Area
    ###################################
    self.lineCollapsibleButton = ctk.ctkCollapsibleButton()
    self.lineCollapsibleButton.text = "Connection Size and Color Thresholding"
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

    #
    # Checkbox to choose whether or not the connection distribution follows a log scale or else a linear distribution
    #
    self.connectionDistCheckBox = qt.QCheckBox()
    self.connectionDistCheckBox.checked = 0
    self.connectionDistCheckBox.setToolTip("If checked, it means that the connection distribution follows a log scale.")
    self.lineconnectFormLayout.addRow("Log Distribution", self.connectionDistCheckBox)

    self.connectionColorTable = slicer.qMRMLColorTableComboBox()
    self.connectionColorTable.nodeTypes = ["vtkMRMLColorTableNode"]
    self.connectionColorTable.addEnabled = True
    self.connectionColorTable.removeEnabled = True
    self.connectionColorTable.noneEnabled = True
    self.connectionColorTable.showHidden = True
    self.connectionColorTable.setMRMLScene( slicer.mrmlScene )
    self.lineconnectFormLayout.addRow("Input Color Map: ", self.connectionColorTable)

    #
    # Threshold node connection strength
    #
    # default values
    self.logic = visuThreeDLogic()
    self.min_strength = 0.0
    self.max_strength = 1.0
    self.connectionThresholdSliderWidget = ctk.ctkRangeWidget()
    self.connectionThresholdSliderWidget.singleStep = 0.01
    self.connectionThresholdSliderWidget.setValues(self.min_strength, self.max_strength)
    self.connectionThresholdSliderWidget.setMaximumValue(self.max_strength)
    self.connectionThresholdSliderWidget.setMinimumValue(self.min_strength)
    self.connectionThresholdSliderWidget.setRange(self.minVal, self.max_strength)
    self.connectionThresholdSliderWidget.setMouseTracking(True)
    self.connectionThresholdSliderWidget.setEnabled(True)
    self.connectionThresholdSliderWidget.setToolTip("Set threshold node value for computing the node value.")
    self.lineconnectFormLayout.addRow("Plot Strength Range:", self.connectionThresholdSliderWidget)

    #
    # Connection min strength spinBox
    #
    # default value for min strength (l: lowest , h: highest)
    self.minStrength_l = 0.0
    self.minStrength_h = 50.0
    self.minConnectionSpinBox = qt.QDoubleSpinBox()
    self.minConnectionSpinBox.singleStep = 0.01
    self.minConnectionSpinBox.setRange(self.minStrength_l, self.minStrength_h)
    self.minConnectionSpinBox.setToolTip("Set minimum connection strength.")
    self.lineconnectFormLayout.addRow("Min Strength:", self.minConnectionSpinBox)

    #
    # Node size max spinBox
    #
    # default value for max size (l: lowest , h: highest)
    self.maxStrength_l = 0.0
    self.maxStrength_h = 100.0
    self.maxConnectionSpinBox = qt.QDoubleSpinBox()
    self.maxConnectionSpinBox.singleStep = 0.01
    self.maxConnectionSpinBox.setRange(self.maxStrength_l, self.maxStrength_h)
    self.maxConnectionSpinBox.setToolTip("Set maximum connection strength.")
    self.lineconnectFormLayout.addRow("Max Strenght:", self.maxConnectionSpinBox) 

    ###################################
    # Advanced Connections scale factors Area
    ###################################
    self.scaleCollapsibleButton = ctk.ctkCollapsibleButton()
    self.scaleCollapsibleButton.text = "Advanced Connection Scale Factors"
    self.layout.addWidget(self.scaleCollapsibleButton)
    # Layout within the collapsible button
    self.scaleconnectFormLayout = qt.QFormLayout(self.scaleCollapsibleButton)

    #Double SpinBox for default scale factor "f" : 
    #computation of value in matrix by the number of connexions * f factor
    self.fscaleDoubleSpinBox = ctk.ctkDoubleSpinBox()
    self.fscaleDoubleSpinBox.setValue(0.000033)
    self.fscaleDoubleSpinBox.setDecimals(6)
    self.fscaleDoubleSpinBox.enabled = True
    self.scaleconnectFormLayout.addWidget(self.fscaleDoubleSpinBox)
    self.scaleconnectFormLayout.addRow("f Scale:", self.fscaleDoubleSpinBox)

    #Double SpinBox for log scale factor "C" : 
    self.logScaleDoubleSpinBox = ctk.ctkDoubleSpinBox()
    self.logScaleDoubleSpinBox.setValue(10)
    self.logScaleDoubleSpinBox.setDecimals(0.)
    self.logScaleDoubleSpinBox.enabled = False
    self.scaleconnectFormLayout.addWidget(self.logScaleDoubleSpinBox)
    self.scaleconnectFormLayout.addRow("C Log Scale:", self.logScaleDoubleSpinBox)

    ###################################
    # Connections
    ###################################
    self.coord = []
    self.index = []
    self.position = []
    self.visu = []
    self.fileImportButton.connect('clicked(bool)', self.on_node_graph_json_load)
    self.inputSelector.connect("nodeActivated(vtkMRMLNode*)", self.on_select)
    self.regionButtons.connect('checkedIndexesChanged()', self.on_regions_checked)
    self.calculateAllFilteredregionsButton.connect('clicked(bool)', self.on_select_all_filtered_regionButtons)
    self.calculateAllregionsButton.connect('clicked(bool)', self.on_select_all_regionButtons)
    self.calculateNoregionsButton.connect('clicked(bool)', self.on_deselect_all_regionButtons)
    self.calculateNoFilteredregionsButton.connect('clicked(bool)', self.on_deselect_all_filtered_regionButtons)
    self.regionSearchBox.connect("textChanged(QString)", self.on_search)
    self.ColorTable.connect("currentNodeChanged(vtkMRMLNode*)", self.on_node_color_clicked)
    self.nodeThresholdSliderWidget.connect("valuesChanged(double, double)", self.sliderbar_changed)
    self.nodeMinSizeSpinBox.connect("valueChanged(double)", self.min_nodesize_changed)
    self.nodeMaxSizeSpinBox.connect("valueChanged(double)", self.max_nodesize_changed)
    self.tableStartSpinBox.connect("valueChanged(double)", self.table_start_changed)
    self.matrixConnectSelector.connect("nodeActivated(vtkMRMLNode*)",self.on_select_matrix)
    self.connectionThresholdSliderWidget.connect("valuesChanged(double, double)", self.sliderbar2_changed)
    self.maxConnectionSpinBox.connect("valueChanged(double)", self.max_connection_changed)
    self.connectionColorTable.connect("currentNodeChanged(vtkMRMLNode*)", self.on_connect_color_clicked)
    self.fscaleDoubleSpinBox.connect("valueChanged(double)", self.on_fscale_changed)
    self.logScaleDoubleSpinBox.connect("valueChanged(double)", self.on_logscale_changed)
    
    # Add vertical spacer
    self.layout.addStretch(1)
    self.header = None
    self.connection_d = None
    self.value = 'None'
    self.on_node_graph_json_load()

# Function linked to header checkbox
  def on_header_select(self, header):
    if self.headerCheckBox.checked == True:
        header = True
    else:
        header = False
    self.logic.set_header_state(header)
    return header

  # Function is called when an input Node table is selected
  def on_select(self, table):
    self.logic.remove_node_actors()
    self.header = self.on_header_select(self.header)
    self.logic.set_header_state(self.header)
    self.logic.set_user_table(table)
    self.logic.create_node_actors()
    self.logic.update()

  # Function is called when a connection matrix is loaded
  def on_connection_d_select(self, connection_d):
    if self.connectionDistCheckBox.checked == True:
        connection_d = True
        self.logScaleDoubleSpinBox.enabled = True
        self.fscaleDoubleSpinBox.enabled = False
    else:
        connection_d = False

    self.logic.set_connection_distribution(connection_d)
    return connection_d

  # We get the connection matrix loaded by the user and read it in the logic
  def on_select_matrix(self, connection_matrix):
    self.logic.remove_line_tube_actors()
    self.connection_d = self.on_connection_d_select(self.connection_d)
    self.logic.set_connection_matrix(connection_matrix)
    self.logic.create_line_actors()
    self.logic.update()

  # When Color map for Nodes is loaded this function is called
  def on_node_color_clicked(self, color_map):    
    self.logic.set_node_color_map(color_map)
    self.logic.update()

  # When Color map for Connections is loaded this function is called
  def on_connect_color_clicked(self, connect_color_map):    
    self.logic.set_connect_color_map(connect_color_map)
    self.logic.update()

  def initializeRegionButtons(self):
    #Insert Items adds each string in filter_visu_hierarchyMap as a checkable combobox, starting at index 0
    self.regionButtons.insertItems(0, self.logic.filter_visu_hierarchyMap(None))
    self.updateRegionButtons()

  # This function automatically ckecks all the filtered boxes. The checkstates: 0-unchecked, 1-partially checked, 2-checked
  # We have to disconnect the checkedIndexesChanged until we are finiched checking all the boxes by default
  # If you foregt to disconnect this signal is called for each checked box.
  def on_search(self, value):
    self.regionButtons.clear()
    self.regionButtons.disconnect('checkedIndexesChanged()', self.on_regions_checked)
    # InsertItems inserts the elements into the drop down combobox menu
    self.regionButtons.insertItems(0, self.logic.filter_visu_hierarchyMap(value))
    for index in range(self.regionButtons.count):
        modelIndex = self.regionButtons.model().index(index, 0, self.regionButtons.rootModelIndex())
        if self.logic.visuHierarchyMapSelected[self.regionButtons.itemText(index)]:
            self.regionButtons.setCheckState(modelIndex, 2)
    self.regionButtons.connect('checkedIndexesChanged()', self.on_regions_checked)
    
  # This is the regionButtons update function
  # We initialize all the regions to checked.
  def updateRegionButtons(self):
    self.regionButtons.disconnect('checkedIndexesChanged()', self.on_regions_checked)
    for index in range(self.regionButtons.count):
        modelIndex = self.regionButtons.model().index(index, 0, self.regionButtons.rootModelIndex())
        if self.logic.visuHierarchyMapSelected[self.regionButtons.itemText(index)]:
            self.regionButtons.setCheckState(modelIndex, 2)
        else:
            self.regionButtons.setCheckState(modelIndex, 0)
    self.regionButtons.connect('checkedIndexesChanged()', self.on_regions_checked)

  # If a checkbox gets checked or unchecked, this function is called.
  def on_regions_checked(self):
    for index in range(self.regionButtons.count):
        modelIndex = self.regionButtons.model().index(index, 0, self.regionButtons.rootModelIndex())
        print("on_regions_checked", self.regionButtons.itemText(index), self.logic.visuHierarchyMapSelected[self.regionButtons.itemText(index)])
        if self.regionButtons.checkState(modelIndex) == 2:
            self.logic.visuHierarchyMapSelected[self.regionButtons.itemText(index)] = True
        else:
            self.logic.visuHierarchyMapSelected[self.regionButtons.itemText(index)] = False
    self.logic.update()

  def on_select_all_filtered_regionButtons(self):
    self.regionButtons.disconnect('checkedIndexesChanged()', self.on_regions_checked)
    for index in range(self.regionButtons.count):
        modelIndex = self.regionButtons.model().index(index, 0, self.regionButtons.rootModelIndex())
        self.regionButtons.setCheckState(modelIndex, 2)
        self.logic.visuHierarchyMapSelected[self.regionButtons.itemText(index)] = True
    self.regionButtons.connect('checkedIndexesChanged()', self.on_regions_checked)
    self.logic.update()    

  def on_select_all_regionButtons(self):
    #self.regionButtons.disconnect('checkedIndexesChanged()', self.on_regions_checked)
    # for index in range(self.regionButtons.count):
    #     modelIndex = self.regionButtons.model().index(index, 0, self.regionButtons.rootModelIndex())
    #     self.regionButtons.setCheckState(modelIndex, 2)
    #     self.logic.visuHierarchyMapSelected[self.regionButtons.itemText(index)] = True
    #     if self.regionButtons.checkState(modelIndex) == 0:
    #         self.regionButtons.setCheckState(modelIndex, 2)
    #         self.logic.visuHierarchyMapSelected[self.regionButtons.itemText(index)] = True
    # self.regionButtons.connect('checkedIndexesChanged()', self.on_regions_checked)
    # self.logic.update()
    for key in self.logic.visuHierarchyMapSelected:
        self.logic.visuHierarchyMapSelected[key] = True
    self.on_select_all_filtered_regionButtons()

  def on_deselect_all_regionButtons(self):
    for key in self.logic.visuHierarchyMapSelected:
        self.logic.visuHierarchyMapSelected[key] = False
    self.on_deselect_all_filtered_regionButtons()

  def on_deselect_all_filtered_regionButtons(self):
    self.regionButtons.disconnect('checkedIndexesChanged()', self.on_regions_checked)
    for index in range(self.regionButtons.count):
        modelIndex = self.regionButtons.model().index(index, 0, self.regionButtons.rootModelIndex())
        self.regionButtons.setCheckState(modelIndex, 0)
        self.logic.visuHierarchyMapSelected[self.regionButtons.itemText(index)] = False
    self.regionButtons.connect('checkedIndexesChanged()', self.on_regions_checked)
    self.logic.update()

  def on_node_graph_json_load(self):
    path_to_json = self.fileImport.currentPath
    try:
        self.logic.remove_node_actors()
        self.logic.set_node_graph_json(path_to_json)
        self.logic.update_node_graph_json()
        self.initializeRegionButtons()
    except Exception as error:
        print ('Error', error, path_to_json)

  # Node slider bar
  def sliderbar_changed(self, newMin, newMax): #node_range):
    self.logic.set_range(newMin, newMax)
    #self.logic.set_sphere_radius(self.max_size)
    self.logic.update()

  # Connection slider bar
  def sliderbar2_changed(self, lineMin, lineMax): #node_range):
    self.logic.set_line_range(lineMin, lineMax)
    self.logic.update()

  def min_nodesize_changed(self, min_node_size):
    self.logic.set_min_size(min_node_size)
    self.logic.update()

  def max_nodesize_changed(self, max_node_size):
    self.logic.set_max_size(max_node_size)
    self.logic.update()

  def table_start_changed(self, table_start):
    self.logic.set_table_start(table_start)
    self.logic.update()

  def min_connection_changed(self, min_connection):
    self.logic.set_min_connection(min_connection)
    self.logic.update()

  def max_connection_changed(self, max_connection):
    self.logic.set_max_connection(max_connection)
    self.logic.update()

  def on_fscale_changed(self, fscale_value):
    self.logic.set_fscale_value(fscale_value)
    self.logic.update()

  def on_logscale_changed(self, log_scale_value):
    self.logic.set_logscale_value(log_scale_value)
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
    self.segmentationNode = slicer.vtkMRMLModelDisplayNode()
    self.index = []
    self.position = []
    self.visu = []

    self.subject_index = 0
    self.min_column = 1
    self.max_column = 79

    self.path_to_json = './Resources/nodeGraph_3D.json'
    self.jep = JEP.json_extract_properties()

    # Initialize an empty filtered VisuHierarchy Map  
    self.filteredVisuHierarchy = {}
    self.visuHierarchyMap = []
    self.checked_regions = []
    self.node_color_map = None
    self.connect_color_map = None
    self.user_table = None
    self.vtk_spheres = []
    self.line_actors = []
    self.tube_actors = []
    self.header = False
    self.connection_d = False
    self.connection_matrix = None
    self.node_size = 7
    self.min_size = 1
    self.max_size = 7
    self.min_strength = 0
    self.max_strength = 7
    self.node_min = 0
    self.node_max = 0.6
    self.line_min = 0
    self.line_max = 1
    self.f = 0.000033
    self.C = 10.0

  def set_node_graph_json(self, path_json):
    if os.path.isfile(path_json):
        self.path_to_json = path_json
    else:
        raise Exception("File does not exist")

  def update_node_graph_json(self):
    self.set_node_graph_array()
    self.set_matrix_row_map()
    self.set_matrix_hierarchy_map()  

  def set_node_graph_array(self):
    self.node_graph_array = []

    with open(self.path_to_json, "r") as json_file:
        self.node_graph_array = json.load(json_file)

  def set_matrix_row_map(self):
    self.matrixRowMap = self.create_matrix_rowMap(self.node_graph_array)

  def set_matrix_hierarchy_map(self):
    self.visuHierarchyMap = self.create_visu_hierarchyMap(self.node_graph_array)
    self.visuHierarchyMapSelected = {}
    for key in self.visuHierarchyMap:
        print("set_matrix_hierarchy_map", key)
        self.visuHierarchyMapSelected[key] = True

  def set_node_color_map(self, color_map):
    self.node_color_map = color_map

  def set_connect_color_map(self, connect_color_map):
    self.connect_color_map = connect_color_map

  def set_range(self,newMin, newMax):
    self.node_min = newMin
    self.node_max = newMax

  def set_line_range(self, lineMin, lineMax):
    self.line_min = lineMin
    self.line_max = lineMax

  def set_user_file(self, user_file):
    self.user_file = user_file
    self.jep = JEP.json_extract_properties()
    self.jep.set_csv_file(self.user_file)
    self.jep.read_csv()

  def set_header_state(self, header):
    self.header = header

  # Set connection check state to check weather or not the user wants a linear distribution of the connections
  # or a log distribution
  def set_connection_distribution(self, connection_d):
    self.connection_d = connection_d

  # Store the values of our Table Node in an array : self.values
  def set_user_table(self, table):
    self.set_table_index()
    self.jep.set_table(table)

  def set_table_start(self, table_start):
    self.min_column = table_start

  def set_max_column(self):
    self.max_column = self.jep.get_max_column()

  # See whether or not the header checkbox is checked
  # if checked: the input table HAS a header : header state = TRUE
  # if not checked: header state = FALSE
  def set_table_index(self):
    self.set_header_state(self.header)
    if self.header == False:
        self.min_column = self.set_table_start(self.min_column)
        self.max_column = self.set_max_column() - 1
    else:
        self.subject_index = 1
        self.min_column = 1
        self.max_column = self.set_max_column()
    return self.subject_index

  def set_checked_regions(self, checked_regions):
    self.checked_regions = checked_regions

  def set_connection_matrix(self, connection_matrix):
    self.connection_matrix = self.jep.set_matrix_connections(connection_matrix)

  def set_fscale_value(self, fscale_value):
    self.f= fscale_value

  def set_logscale_value(self, log_scale_value):
    self.C= log_scale_value

  def update(self):
    self.set_sphere_radius(self.node_max)
    self.set_node_actors_properties()
    if self.connection_matrix is not None:
        self.set_line_connection(self.line_max)
        self.set_line_actors_properties()
    self.render()

  # Map that indexes the json file by Matrix Row
  def create_matrix_rowMap(self, node_graph_array):
      d2 = {}   
      self.node_array = []

      # i is the index, node is the element
      for i,node in enumerate(node_graph_array):
        if node["MatrixRow"] != -1:
          d2[node["MatrixRow"]] = node
          self.node_array.append(d2[node["MatrixRow"]])
      return d2 

  # Map that indexes the json file by visuHierarchy name
  def create_visu_hierarchyMap(self, node_graph_array):
      d3 = {}      

      # i is the index, node is the element
      for i,node in enumerate(node_graph_array):
        if(node["VisuHierarchy"] not in d3):
            d3[node["VisuHierarchy"]] = []
        d3[node["VisuHierarchy"]].append(node)        
      return d3

  # filter function linked to the search text for visuHierarchy checkbox
  def filter_visu_hierarchyMap(self, search_text):
    visuHierarchyMapMatches = []

    if(search_text is not None):
        regex = ".*" + search_text + ".*"
        for key in self.visuHierarchyMap:         
            if re.match(regex, key) is not None:
                visuHierarchyMapMatches.append(key)
    else:
        for key in self.visuHierarchyMap:
            visuHierarchyMapMatches.append(key)
    return visuHierarchyMapMatches

  def set_min_size(self, min_node_size):
    self.min_size = min_node_size

  def set_max_size(self, max_node_size):
    self.max_size = max_node_size

  def set_max_connection(self, max_connection):
    self.max_strength = max_connection

  def get_node_max(self, node_max):
    self.node_max = node_max

  def set_node_size(self):
    self.node_size = [self.min_size, self.max_size]

  def create_node_actors(self):
    lm = slicer.app.layoutManager()
    threeDView = lm.threeDWidget(0).threeDView()
    self.renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
    
    # Generate an empty list to store each Sphere
    self.vtk_spheres = []
    for node in self.node_array:

        # Dictionnary of all the spheres
        sphere = {}

        sphere['source'] = vtk.vtkSphereSource()
        sphere['source'].SetCenter(node['coord'])
        sphere['source'].SetRadius(7)

        sphere['name'] = node['VisuHierarchy']

        sphere['actor'] = vtk.vtkActor()
        sphere_mapper = vtk.vtkPolyDataMapper()
        
        sphere_mapper.SetInputConnection(sphere['source'].GetOutputPort())
        sphere['actor'].SetMapper(sphere_mapper)
        
        self.vtk_spheres.append(sphere)

        self.renderer.AddActor(sphere['actor'])

  def render(self):
    lm = slicer.app.layoutManager()
    threeDView = lm.threeDWidget(0).threeDView()
    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
    renderer.Render()

  def set_sphere_radius(self, node_max):

    value_list = self.jep.get_subject_values(self.subject_index, self.min_column, self.max_column)
    len_sphere_actors = len(self.vtk_spheres)

    for index in range(len_sphere_actors):

        if(index < len(value_list)):
            prop_value = (value_list[index])
            vtk_sphere = self.vtk_spheres[index]

            print("set_sphere_radius", vtk_sphere['name'], self.visuHierarchyMapSelected[vtk_sphere['name']])

            if (prop_value < self.node_min or not self.visuHierarchyMapSelected[vtk_sphere['name']]):  
                vtk_sphere['source'].SetRadius(self.min_size)
                vtk_sphere['actor'].SetVisibility(False)

            else:   
                vtk_sphere['source'].SetRadius(((prop_value - self.node_min)/self.node_max)*(self.max_size - self.min_size) + self.min_size)
                vtk_sphere['actor'].SetVisibility(True)

  def set_region_filter(self):
    value_list = self.jep.get_subject_values(self.subject_index, self.min_column, self.max_column)
    len_sphere_actors = len(self.vtk_spheres)
    sphere_name = []

    for index in range(len_sphere_actors):

        if(index < len(value_list)):
            prop_value = (value_list[index])
            vtk_sphere = self.vtk_spheres[index]
            sphere_name.append(vtk_sphere['name'])

            for r in self.checked_regions:
                print('1', r, '2:', self.checked_regions, '3:', index)
                if r in sphere_name:
                    if r == sphere_name[index]:
                #if r in sphere_name:
                        vtk_sphere['actor'].SetVisibility(True)
                        print('sphere name:', r)
                        print('checked regions LIST:', self.checked_regions)
                    else:
                        vtk_sphere['actor'].SetVisibility(False)

  def set_node_actors_properties(self):
    value_list = self.jep.get_subject_values(self.subject_index, self.min_column, self.max_column)
    self.range_list = [self.node_min, self.node_max]
    if self.vtk_spheres and self.node_color_map and value_list:        

        len_sphere_actors = len(self.vtk_spheres)
        lookup_table = self.node_color_map.GetLookupTable()        
        lookup_table.SetRange(self.node_min, self.node_max)

        for index, sphere in enumerate(self.vtk_spheres):
            
            color = [0,0,0]
            lookup_table.GetColor(value_list[index],color)
            sphere['actor'].GetProperty().SetColor(color) 

  def remove_node_actors(self):
    len_sphere_actors = len(self.vtk_spheres)
    for index in range(len_sphere_actors):
      vtk_sphere = self.vtk_spheres[index]
      self.renderer.RemoveActor(vtk_sphere['actor'])
    self.vtk_spheres.clear()

  def create_line_actors(self):

    lm = slicer.app.layoutManager()
    threeDView = lm.threeDWidget(0).threeDView()
    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()

    self.line_actors = []
    self.tube_actors = []
    self.node_graph_actors_lookup = -1*np.ones([len(self.node_array), len(self.node_array)], dtype=int)

    # By default each connection is connected to every node
    for i, node_i in enumerate(self.node_array):
        current_line_actors = []

        for j in range(i + 1, len(self.node_array)):
            node_j = self.node_array[j]
            self.list_index = i
            self.node_graph_actors_lookup[i][j] =  len(self.line_actors)
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
            tube['filter'].SetNumberOfSides(3)

            #create mapper and actor
            tube['actor'] = vtk.vtkActor()
            tube['mapper'] = vtk.vtkPolyDataMapper()

            tube['mapper'].SetInputConnection(tube['filter'].GetOutputPort())
            tube['actor'] .GetProperty().SetOpacity(1)
            tube['actor'] .SetMapper(tube['mapper'])

            renderer.AddActor(tube['actor'])

            self.tube_actors.append(tube)

  def set_line_connection(self, line_max):
    self.connection_matrix_np = np.array(self.connection_matrix)

    # Iterate over rows and columns of the connection matrix
    for i,row in enumerate(self.connection_matrix_np):
      for j,val in enumerate(row): 

        # In order to keep the same dimensions as when we created the connections (line +tubes)
        # we call our actor lookup matrix and only look at the upper level of this lookup matrix
        # that has values in the upper triangle and -1 on the diagonal and the lower triangle of the
        # matrix 
        if self.node_graph_actors_lookup[i][j] != -1 :
          actor_index = self.node_graph_actors_lookup[i][j]
          line = self.line_actors[actor_index]
          tube = self.tube_actors[actor_index]
          # Because we iterate over the rows and columns of the connection matrix we also
          # have to access the spheres for each row (i) and column (j)
          sphere_i = self.vtk_spheres[i]
          sphere_j = self.vtk_spheres[j]
          self.x = float(val)
          self.set_connection_d()

          # Condition: If the value in the matrix is zero then there is no connection
          # We set the visibility of the line and tubes to False
          # NB: This doesn't remove the actor from the renderer
          if (float(val) == 0):
            line['actor'].SetVisibility(False)
            line['actor'].GetProperty().SetLineWidth(self.line_min)
            tube['filter'].SetRadius(self.line_min)
            tube['actor'].SetVisibility(False)

          elif (self.connection_value) < self.line_min:
            line['actor'].SetVisibility(False)
            line['actor'].GetProperty().SetLineWidth(self.line_min)
            tube['filter'].SetRadius(self.line_min)
            tube['actor'].SetVisibility(False)

          elif (self.connection_value) > self.line_max:

            if sphere_i['actor'].GetVisibility() == 1 and sphere_j['actor'].GetVisibility() == 1:
                line['actor'].SetVisibility(True)
                tube['filter'].SetRadius(self.line_max)
                tube['actor'].SetVisibility(True)
            else: 
                line['actor'].SetVisibility(False)
                tube['filter'].SetRadius(self.line_min)
                tube['actor'].SetVisibility(False)

          else: 
            if sphere_i['actor'].GetVisibility() == 1 and sphere_j['actor'].GetVisibility() == 1:
                line['actor'].SetVisibility(True)
                tube['filter'].SetRadius(((self.connection_value - self.line_min)/self.line_max)*(self.max_strength - self.min_strength) + self.min_strength)
                tube['actor'].SetVisibility(True) 
            else:
                line['actor'].SetVisibility(False)   
                tube['filter'].SetRadius(self.line_min)
                tube['actor'].SetVisibility(False)  

  # Set connection distribution
  # if checkbox is checked, then we display the connections sizes in a log scale
  # if checkbox is not checked , default value is a linear scale (but values vary little, so only the color would be a good indicator)
  def set_connection_d(self):
    self.set_connection_distribution(self.connection_d)
    self.connection_matrix_np = np.array(self.connection_matrix)
    len_line_actors = len(self.line_actors)
    self.conn_colors = []

    if self.x!= 0 :
        compute_connections = (len_line_actors*(len_line_actors-1))/2

        if self.connection_d == False:
            self.connection_value = self.x*compute_connections*self.f
            self.conn_colors.append(self.connection_value)

        else:
            self.connection_value = (math.log10(self.x)+self.C)/self.C
            self.conn_colors.append(self.connection_value)

  def set_line_actors_properties(self):
    connection_matrix_np = np.array(self.connection_matrix)
    vals = []
    self.set_connection_distribution(self.connection_d)
    for i,row in enumerate(connection_matrix_np):
      for j,val in enumerate(row):   

        if self.line_actors and self.tube_actors and self.connect_color_map: #and matrix:        
            len_line_actors = len(self.line_actors)
            lookup_table = self.connect_color_map.GetLookupTable()        
            lookup_table.SetRange(self.line_min, self.line_max)

            if (self.node_graph_actors_lookup[i][j] != -1) and (float(val) != 0):
              actor_index = self.node_graph_actors_lookup[i][j]
              tube = self.tube_actors[actor_index]
              self.x = float(val)
              self.set_connection_d()
              vals.append(self.connection_value)

              for index in range(len(vals)):
                  color = [0,0,0]
                  lookup_table.GetColor(vals[index], color)
                  tube['actor'].GetProperty().SetColor(color)

  def remove_line_tube_actors(self):
    len_line_actors = len(self.line_actors)
    for index in range(len_line_actors):
      vtk_line = self.line_actors[index]
      vtk_tube = self.tube_actors[index]
      self.renderer.RemoveActor(vtk_line['actor'])
      self.renderer.RemoveActor(vtk_tube['actor'])
    self.line_actors.clear()
    self.tube_actors.clear()

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
    #visu_logic.set_user_table(self.user_table)
    #visu_logic.set_user_file('/work/maria5/EBDS_CIVILITY/DataShare/TestMatricesForVisualization/AAL78/PerNodeMetrics/Conte_EigenVectorCentrality_4Yr_AAL78Regions.csv')
    #visu_logic.set_user_file('/Users/Wieke/Documents/visuThreeD/neo-0042-4year_AvgSym_normFull.csv')
    # visu_logic.create_node_actors()
    # visu_logic.create_line_actors()
    # visu_logic.update()
    #visu_logic.set_node_range()

   