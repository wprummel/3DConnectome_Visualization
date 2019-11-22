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

  def set_csv_file(self, csv_file):
    self.csv_file = csv_file

  # Read csv as a dictionary
  def dict_read_csv(self):

    with open(self.csv_file, "r") as csv_file:
        self.csv_content = csv.DictReader(csv_file, delimiter=',')
        #self.csv_content = csv.reader(csv_file, delimiter=',')

        order_dict = []

        for i, row in enumerate(self.csv_content):

          print(i, json.dumps(row, sort_keys=True, indent=4))
          order_dict.append({'subjects' : i, 'names' :{'name': row}})
          #print (order_dict)

          #order_dict = (i, json.dumps(row, sort_keys=True, indent=4))
          #print (order_dict)
        return order_dict
        #return


  # Read csv as string and ask user for an interval : begin and end 
  def read_csv(self):

    self.csv_content = []
    with open(self.csv_file, "r") as csv_file:
        # self.csv_content = csv.DictReader(csv_file, delimiter=',')
        self.csv_content = csv.reader(csv_file, delimiter=',')


    return self.csv_content
        

  def get_subject_content(self):

    with open('csv_to_json.json', 'w') as f:

        data = self.dict_read_csv()
        json.dump(data, f, sort_keys=True, indent=4)

  def dict_write_json(self):
    for i, row in enumerate(self.csv_content):
      #print(i, json.dumps(row, sort_keys=True, indent=4))
      # subject.append({'subjects' : i, 'names' :{'name': row}})  
      out_name = os.path.join(out_directory, "subject_.json" %i)
      with open(out_name, 'w') as f:
        json.dump(row, f, sort_keys=True, indent=4)

  def get_subject(self, row):

    return self.csv_content[row]

  def get_nodeName_index(self):

    index = []

    with open('subject_num.json', 'r') as jfile:

      subject_nb = json.load(jfile)

      for i in subject_nb.items():

        index.append(i)
      print (index)
      return index

    #     line_count = 2
    #     i=2
    #     subject = []
    #     j=1

    #     for j in self.eigenVectCenter:

    #         #subject.append({", ".join(j)})
    #         subject.append(j)

    #         #subject.append(self.eigenVectCenter[2][j])
    #     #for row in self.eigenVectCenter:

    #     # if line_count == 2:

    #     #     print({", ".join(row)})
    #             #line_count += 1
            
    #         # else:

    #         #     print( {row[2]})
    #         #     line_count += 1
    # subjectCurrent = subject[1]

    # del subjectCurrent[0]
    # del subjectCurrent[0]
    # print subjectCurrent[1]
    # print ('Current subject is :', len(subjectCurrent))
    # print len(subjectCurrent)
    # #print (len(subject[1]))
    # return subjectCurrent
  
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


