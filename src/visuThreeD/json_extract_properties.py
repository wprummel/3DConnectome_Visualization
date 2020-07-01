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
    self.output_directory = "out"
    self.csv_content = []
    self.matrix_content = []

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

  # Extracts the values from the table loaded trough the Data Module
  # Data is stored in a matrix/table, 
  # table_content is of same type as csv_content in read_csv()
  def set_table(self, table):
    table_content = []
    header_content = []
    self.max_column = table.GetNumberOfColumns()

    for i in range(table.GetNumberOfColumns()):
      header_content.append(table.GetColumnName(i))

    table_content.append(header_content)

    for i in range(table.GetNumberOfRows()):
      row_content = []
      for j in range(table.GetNumberOfColumns()):
        row_content.append(table.GetCellText(i, j))
      table_content.append(row_content)

    print ('list of property values', table_content)
    self.csv_content = table_content
    #self.matrix_content = table_content

  def set_matrix_connections(self, connection_matrix):
    matrix_content = []
    header_content = []

    for i in range(connection_matrix.GetNumberOfColumns()):
      header_content.append(connection_matrix.GetColumnName(i))

    matrix_content.append(header_content)

    for i in range(connection_matrix.GetNumberOfRows()):
      row_content = []
      for j in range(connection_matrix.GetNumberOfColumns()):
        row_content.append(connection_matrix.GetCellText(i, j))
      matrix_content.append(row_content)

    print ('matrix content values', matrix_content)
    self.matrix_content = matrix_content
    #return [float(v) for v in matrix_content[0]]
    #return matrix_content

  def get_connections_row(self):
    #self.set_table(connection_matrix)
    l = len(self.matrix_content) 
    print ('len csv.content', l)
    # if(index < len(self.matrix_content)): 
    #   print('content isssss', self.matrix_content[index]) 
    #   return self.matrix_content[index]
    #return []
    return self.matrix_content

  def get_subject_content(self, index):
    l = len(self.csv_content) 
    print ('len csv.content', l)
    if(index < len(self.csv_content)): 
      print('content isssss', self.csv_content[index]) 
      return self.csv_content[index]
    return []

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

  def get_subject_values(self, subject_index, min_column, max_column):
    subject_content = self.get_subject_content(subject_index)
    print("subject_content", subject_content)
    print("subject_content", len(subject_content))
    if(len(subject_content) > min_column):
      #return subject_content[min_column:max_column]
      return [float(v) for v in subject_content[min_column:max_column]]
    return []

  def get_connection_rows(self, row_index):
    #row_content = self.get_connections_row(0)
    row_content = self.matrix_content[row_index]
    print("row_content", row_content)
    print("row_content", len(row_content))
    if(len(row_content) > 0):
      #return subject_content[min_column:max_column]
      return [float(v) for v in row_content]
    return []