#!/usr/bin/env python3
import csv
import json
import os
"""
This script extracts properties from the initial json file 
in order to associate an index (Matrix Rox) form the json, 
with the corresponding node degree form another file
"""
#self.path_to_json ='/work/wprummel/Tools/Test-files/Connectome_3D_Visualization/nodeGraph_3D.json'
# self.user_file = '/work/maria5/EBDS_CIVILITY/DataShare/TestMatricesForVisualization/AAL78/PerNodeMetrics/Conte_EigenVectorCentrality_4Yr_AAL78Regions.csv'

# #self.nodeGraphArray = []

# self.user_csvFile = open(self.user_file, "r")
# read_csvFile(self.user_csvFile)

#def read_csvFile(self, user_csvFile):

class json_extract_properties():

  def __init__(self):
    self.csv_file = ''
    self.subject_num = 10
    self.output_directory = "out"
    self.csv_content = []
    self.min = 2
    self.max = 80

  def set_csv_file(self, csv_file):
    self.csv_file = csv_file

  def set_output_directory(self, outdir):
    self.output_directory = outdir    

  # Read csv as string and ask user for an interval : begin and end 
  def read_csv(self):

    self.csv_content = []
    with open(self.csv_file, "r") as csv_file:
        # csv_reader = csv.DictReader(csv_file, delimiter=',')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
          self.csv_content.append(row)

  def get_subject_content(self, index):
    
    if(index < len(self.csv_content)):      
      return self.csv_content[index]

# Store the corresponding indexes in a list
  def store_index_list(self):

    with open('translation_table.json', 'r') as tr:

      table = json.load(tr)
      index = []

      for value in table.values():

        index.append(value)

      #print (index)
      return index

  # Write each subject data to a different json file 
  def dict_write_json(self):
    for i, row in enumerate(self.csv_content):
      #print(i, json.dumps(row, sort_keys=True, indent=4))
      # subject.append({'subjects' : i, 'names' :{'name': row}})        
      out_name = os.path.join(self.output_directory , "subject_" + str(i) + ".json")

      with open(out_name, 'w') as f:
        json.dump(row, f, sort_keys=True, indent=4)

  # Return the corresponding values (eigen or node degree for example)
  def get_values(self):

    i = self.subject_num

    with open('/work/wprummel/data/maria5/EBDS_CIVILITY/subject_' + str(i) + '.json', 'r') as sub:

      value = json.load(sub)
      print (len(value))
      # ask the user for a begin and a end value
      value = value[self.min:self.max]
      print (value)
  
  def write_json(self):

    #node_properties = []
    node_properties = {} 
    #node_properties['MatrixRow'] = [self.get_node_index(self.nodeGraphArray)]
    #matrixIndex = self.get_node_index(self.nodeGraphArray)
    #matrixIndex.remove(-1)

    eigenVect = self.read_csvFile(self.user_csvFile)

    for index,eigen in enumerate(eigenVect, start =1):

        #node_properties.append({'MatrixRow' : index , 'properties' : {'scalars' : {'eigenVectCenter' : eigen}}})
        node_properties = {'MatrixRow' : index , 'properties' : {'scalars' : {'eigenVectCenter' : eigen}}}
        node_properties.update(node_properties)

    print (node_properties) 
    #return node_properties

    # convert node_properties [list] to dictionary 
    #it = iter(node_properties)
    #dict_prop = dict(zip(it,it)) 

    # convert into json
    json_prop = json.dumps(node_properties, sort_keys=True, indent=4)
    print (json_prop)


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

  def sort_by_matrixRow(self, nodeGraphArray):
    
    row = {}

    for i,node in enumerate(self.nodeGraphArray):

    	row[node["MatrixRow"]] = node        

    return row


