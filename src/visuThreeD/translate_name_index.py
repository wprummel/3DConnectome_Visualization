#!/usr/bin/env python3
import json

""" 
This file translates the name of the nodes to the index.
Therfore if the nodeGraph_3D.json uses a different name, we can have the translation with the names in the csv file. 
The index (Matrix Row) never changes.

"""
class translate_name_index():

	def name_to_index(self):
		names = ['PreCG.L','PreCG.R','SFGdor.L','SFGdor.R','ORBsup.L','ORBsup.R','MFG.L','MFG.R','ORBmid.L','ORBmid.R','IFGoperc.L','IFGoperc.R',
		'IFGtriang.L','IFGtriang.R','ORBinf.L','ORBinf.R','ROL.L','ROL.R','SMA.L','SMA.R','OLF.L','OLF.R','SFGmed.L','SFGmed.R','ORBsupmed.L',
		'ORBsupmed.R','REC.L','REC.R','INS.L','INS.R','ACG.L','ACG.R','DCG.L','DCG.R','PCG.L','PCG.R','PHG.L','PHG.R','CAL.L','CAL.R','CUN.L',
		'CUN.R','LING.L','LING.R','SOG.L','SOG.R','MOG.L','MOG.R','IOG.L','IOG.R','FFG.L','FFG.R','PoCG.L','PoCG.R','SPG.L','SPG.R','IPL.L','IPL.R',
		'SMG.L','SMG.R','ANG.L','ANG.R','PCUN.L','PCUN.R','PCL.L','PCL.R','HES.L','HES.R','STG.L','STG.R','TPOsup.L','TPOsup.R','MTG.L','MTG.R',
		'TPOmid.L','TPOmid.R','ITG.L','ITG.R']
		print (names[1])

		translation_dict = {}

		for index,name in enumerate(names, start=1):
		    translation_dict[name] = index

		with open('translation_table.json', 'w') as json_file:

		    json.dump(translation_dict, json_file, sort_keys=True, indent=4)

