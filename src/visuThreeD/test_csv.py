import json_extract_properties as JEP

jep = JEP.json_extract_properties()

jep.set_csv_file('/work/maria5/EBDS_CIVILITY/DataShare/TestMatricesForVisualization/AAL78/PerNodeMetrics/Conte_EigenVectorCentrality_4Yr_AAL78Regions.csv')

jep.read_csv()

print(jep.get_subject_content(1))

jep.set_output_directory('/work/wprummel/data/maria5/EBDS_CIVILITY')

jep.dict_write_json()

jep.get_values()


