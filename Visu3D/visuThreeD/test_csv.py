import json_extract_properties as JEP

jep = JEP.json_extract_properties()

jep.set_csv_file('/work/maria5/EBDS_CIVILITY/DataShare/TestMatricesForVisualization/AAL78/PerNodeMetrics/Conte_EigenVectorCentrality_4Yr_AAL78Regions.csv')

jep.dict_read_csv()

jep.get_subject_content()

jep.dict_write_json()

jep.get_nodeName_index()

#jep.name_to_index()

