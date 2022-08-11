#!/usr/bin/env python
# Script: Script reads BPM parameters from FG screen
# Author: M.Fedurin, T.Morris 06/24/2022

# Version: 0.0
# Last Update: 2022/07/11 (M.Fedurin, Lines:198,207,209,252 "tol" changed to 1e+1)

# Notes:

import time
#import atf_db  #for ATF database operations
import atf_db_py3x as atf_db
import datetime
import pandas as pd
import numpy as np

#import pyvisa
#import numpy as np

host_name = '172.16.82.101'
port_name = 1505

atf_db.host_connect(host_name,port_name)  # Generate socket

print("version of Mon 27 Jun 2022 03:47:41 PM EDT ")

def ReadLaserEnergy():

    LaserEnergy = atf_db.get_real(atf_db.get_channel_index("RT_DATABASE::JOULE;RLE;LASER_ENERGY"))
    return LaserEnergy

def WriteLaserEnergy(a):
    stra = str(a)
    atf_db.put_real(atf_db.get_channel_index("NEWPORT_DB::YAG_INTENSITY;DESIRED_MOVEMENT_NATIVE_UNITS"), a)
#    atf_db.put_real(AtfDB.getchix("NEWPORT_DB::YAG_INTENSITY;DESIRED_MOVEMENT_NATIVE_UNITS"), '+5')
#do i need time in between here?
    atf_db.put_binary(atf_db.get_channel_index("NEWPORT_DB::YAG_INTENSITY;START_STOP_MOTION_CTRL"),"START")
    time.sleep(3)


LaserEnergyRead = ReadLaserEnergy()

print(" ")
print("Laser Energy = ", LaserEnergyRead)
print(" ")

fgN=3

def CameraSwitchFG3(POPN):
	atf_db.put_integer(atf_db.get_channel_index("RT_DATABASE::VID_SWITCH;CMM;VID_MON_03_MUX"),POPN)
	time.sleep(1)

def MovePOPIN(POPN,Direction):
	atf_db.put_binary(atf_db.get_channel_index("RT_DATABASE::POPCTL" + POPN + ";CPU;CTL_REQ_POP_UP_CKT_"+ POPN),Direction)
	

def GetPOPIN(POPN):
	return atf_db.get_binary(atf_db.get_channel_index("RT_DATABASE::POPCTL" + POPN + ";RPU;RDBK_REQ_POP_UP_CKT_"+ POPN))

# POPINLIST = [POPIN_NAME, POIPIN_#, POPIN_CAM_#],[]]
POPINLIST = [['LTR','21','6'],['LPOP1','11','2'],['HPOP1','18','4'],['HPOP2','14','75'],['CHIC_UP','36','54'],['CHIC_DOWN','36','55'],['HPOP3','13','24'],['HPOP4','12','5'],['HPOP5','38','76'],['HPOP6','39','77']]


pop_in_dict = {}

for name, n_pop, n_cam in POPINLIST:

	pop_in_dict[name] = {}
	pop_in_dict[name]['n_pop'] = n_pop
	pop_in_dict[name]['n_cam'] = n_cam

def pop_and_switch(name):


	MovePOPIN(pop_in_dict[name]['n_pop'], 'INSERT')
	CameraSwitchFG3(pop_in_dict[name]['n_cam'])

	for _name, d in pop_in_dict.items():

		if _name == name: continue

		if GetPOPIN(d['n_pop']) == "'INSERT'":

			print(f'retracting {_name}...') 
			MovePOPIN(d['n_pop'], 'RETRACT')
		
	print(f'inserting {name}...')
	time.sleep(1)



def ReadFG(fgN):
   fgname = "FRAME" + str(fgN) + "_DB::FGR" + str(fgN) + ";"
   xpos = atf_db.get_real(atf_db.get_channel_index(fgname+"RCX;CENTROID_X"))
   ypos = atf_db.get_real(atf_db.get_channel_index(fgname+"RCY;CENTROID_Y"))
   xsig = atf_db.get_real(atf_db.get_channel_index(fgname+"RSX;SIGMA_X"))
   ysig = atf_db.get_real(atf_db.get_channel_index(fgname+"RSY;SIGMA_Y"))
#   pixsum = atf_db.get_real(atf_db.get_channel_index(fgname +"RM00;SUM_PIXELS"))
   return [xpos,ypos,xsig,ysig]

def StopFGSavePicRunFG(fgN,FullPathFileName):
   fgname = "FRAME" + str(fgN) + "_DB::FGR" + str(fgN) + ";"
   ReadButtonStatus = atf_db.get_binary(atf_db.get_channel_index(fgname+"RRS;RUN_STOP_READBACK"))
   print('FG'+str(fgN)+' is at: '+str(ReadButtonStatus))
   time.sleep(1)
   PushButton = atf_db.put_binary(atf_db.get_channel_index(fgname+"CRS;RUN_STOP_CONTROL"),"STOP")
   time.sleep(1) 
   ReadButtonStatus = atf_db.get_binary(atf_db.get_channel_index(fgname+"RRS;RUN_STOP_READBACK"))
   print('FG'+str(fgN)+' is now : '+str(ReadButtonStatus))
   FileNameLog = atf_db.put_string(atf_db.get_channel_index(fgname+"CIFN;IMAGE_FILE_NAME"),FullPathFileName)
   time.sleep(1)
   PushButtonSave = atf_db.put_binary(atf_db.get_channel_index(fgname+"CSIF;SAVE_IMAGE_FILE_CTRL"),'SAVING')
   time.sleep(3) 
   PushButton = atf_db.put_binary(atf_db.get_channel_index(fgname+"CRS;RUN_STOP_CONTROL"),"RUN")
   time.sleep(1) 
   







# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~* VaryCurrent PART START *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

def PSCurrentReadSet(ChannelName,db=''):

	return atf_db.get_real(atf_db.get_channel_index(f'{db}::' + str(ChannelName) + ";CDS;SET_CURRENT_SETPT"))


def PSCurrentSet(ChannelName,CurrentSet,db=''):

	atf_db.put_real(atf_db.get_channel_index(f'{db}::' + str(ChannelName) + ";CDS;SET_CURRENT_SETPT"),CurrentSet)

def PSCurrentRead(ChannelName,db='abc'):

    return atf_db.get_real(atf_db.get_channel_index(f"{db}::" + str(ChannelName) + ";RAS;RB_CURRENT_SETPT"))
  

# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~* VaryCurrent PART START *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

channel_names_full_Hline = { 'HPOP1' : { "LT1HX" : "CAEN3",
	         	     "LT1VX" : "CAEN2",
	         	     "LT2HX" : "CAEN1",
	         		"LT2VX" : "CAEN4",
		 		 "TK1H" : "CAEN13",
	          	   	 "TK1V" : "CAEN14",
	         		 "TK2H" : "CAEN15", 
	          		 "TK2V" : "CAEN16",
 		  		 "TK3H" : "CAEN17",
	          		 "TK3V" : "CAEN18"},

		 'HPOP2' : { "HT1HX" : "DARL1",
	        	     "HT1VX" : "DARL2",
	       			 "HT2HX" : "DARL3",
	       			 "HT2VX" : "DARL4",
				  "HQ1" : "DARL149",
		                  "HQ2" : "DARL150",
				  "HQ3" : "DARL151"},

		 'HPOP3' : {},

		 'HPOP4' : { "HT3HX" : "DARL9",
	        		 "HT3VX" : "DARL10",
	         		"HT4HX" : "DARL27",
	         		"HT4VX" : "DARL28",
		  		 "HQ4" : "DARL152",
		  		 "HQ5" : "DARL153",
		  		 "HQ6" : "DARL154"},
		  'HPOP5' : {},
		  'HPOP6' : {  "HT3HX" : "DARL29",
	        		 "HT3VX" : "DARL30",
	         		"HT4HX" : "DARL31",
	         		"HT4VX" : "DARL32",
		  		 "HQ4" : "DARL155",
		  		 "HQ5" : "DARL156",
		  		 "HQ6" : "DARL157"}
			
	         
	        }


channel_names = { 'HPOP2' : { "HT1HX" : "DARL1",
	        	      "HT1VX" : "DARL2",
	       			 "HT2HX" : "DARL3",
	       			 "HT2VX" : "DARL4",
				  "HQ1" : "DARL149",
		                  "HQ2" : "DARL150",
				  "HQ3" : "DARL151"},

		 'HPOP3' : {},

		 'HPOP4' : { "HT3HX" : "DARL9",
	        		 "HT3VX" : "DARL10",
	         		"HT4HX" : "DARL27",
	         		"HT4VX" : "DARL28",
		  		 "HQ4" : "DARL152",
		  		 "HQ5" : "DARL153",
		  		 "HQ6" : "DARL154"},
		  'HPOP5' : {},
		  'HPOP6' : {  "HT3HX" : "DARL29",
	        		 "HT3VX" : "DARL30",
	         		"HT4HX" : "DARL31",
	         		"HT4VX" : "DARL32",
		  		 "HQ4" : "DARL155",
		  		 "HQ5" : "DARL156",
		  		 "HQ6" : "DARL157"}
			
	         
	        }


POP_list = ['HPOP1', 'HPOP2', 'HPOP3', 'HPOP4', 'HPOP5', 'HPOP6']


channel_dict = {}


dp_max  = 0.2
dp_step = 0.05

for pop, channels in channel_names.items():

	n_pop = int(pop[-1])

	for tag, name in channels.items():

		channel_dict[tag] = {}
		channel_dict[tag]['name']  = name
		channel_dict[tag]['n_pop'] = n_pop
		channel_dict[tag]['tol']   = 1e+1

		if name[:4] == 'CAEN': 
			channel_dict[tag]['db'] = 'CAEN_DB'
		
		else: 
			channel_dict[tag]['db'] = 'RT_DATABASE'

		if name[:4] == 'PTEN':
			channel_dict[tag]['tol'] = 1e+1	
		if name[:4] == 'DARL':
			channel_dict[tag]['tol'] = 1e+1		

		channel_dict[tag]['orig'] = PSCurrentReadSet(name, channel_dict[tag]['db']) #changed "PSCurrentRead" to "PSCurrentReadSet" ; M.Fedurin

		channel_dict[tag]['p_list'] = channel_dict[tag]['orig'] + np.arange(-dp_max, dp_max + 1e-6, dp_step)

		#print(channel_dict[tag])
		print(tag, name)




FileName = "C:/Images/AE124/20220711/2022071542_HPOP1_"

fgN=3
#


print(channel_dict)


timestamp = int(time.time())


ps_columns = list(channel_dict.keys())



Files = 'SavedFileName'



POP_cols = ['xpos', 'ypos', 'xsig', 'ysig', 'file']

metadata = pd.DataFrame(columns=['timestamp', *ps_columns, *[f'{POP}_{col}' for POP in POP_list for col in POP_cols]])

print(metadata.columns)


ps_tol = 1e-1

min_wait_time = 1e-1 
max_wait_time = 2e0

def put_complete(ps, set_point, verbose=True):

	name, db = ps['name'], ps['db']

	abs_tol = np.abs(ps['tol'] * (PSCurrentReadSet(name, db) - set_point)) #changed "PSCurrentRead" to "PSCurrentReadSet" ; M.Fedurin

	PSCurrentSet(name, set_point, db)
	t0 = time.time()
	while True:
		elapsed = time.time() - t0
		if elapsed > max_wait_time: break		
		if elapsed > min_wait_time:
			if np.abs(PSCurrentReadSet(name, db) - set_point) < abs_tol: #changed "PSCurrentRead" to "PSCurrentReadSet" ; M.Fedurin
				break
			#print(PSCurrentReadSet(name, db), set_point, db)
		time.sleep(1e-1)
	t1 = time.time()
	if verbose: print(f'set {name} to {set_point:.03e} +/- {abs_tol:.01e} ({PSCurrentRead(name, db):.03e}) in {1e3*(t1-t0):.00f}ms')

	
from datetime import datetime

now = datetime.now()

print(metadata.columns)

	
dirname = f"C:/Images/AE124/{now.year}{now.month:>02}{now.day:>02}/"

POP_metadata = {}

for POP in POP_list:

	n_pop = int(POP[-1])

	pop_and_switch(POP)

	#POP_metadata[POP] = metadata.copy()

	#scan_id = 0

	for tag, ps in channel_dict.items():

		if not ps['n_pop'] == n_pop: continue

		for p in ps['p_list']:

			scan_id = len(metadata)
					
			put_complete(ps, p)

			filetimestamp = int(time.time())

			filename = f'{filetimestamp}_{POP}.asc'

			StopFGSavePicRunFG(3, dirname + filename)

			if len(metadata) <= scan_id: metadata.loc[scan_id] = np.nan
			metadata.loc[scan_id, ['timestamp', *ps_columns]] = time.time(),*[PSCurrentReadSet(ps['name'], ps['db']) for ps in channel_dict.values()] #changed "PSCurrentRead" to "PSCurrentReadSet" ; M.Fedurin
			metadata.loc[scan_id, [f'{POP}_{col}' for col in POP_cols]] = *ReadFG(fgN), filename
			put_complete(ps, ps['orig'])
			#scan_id += 1


metadata.to_csv(f'{timestamp}.csv')


for tag, ps in channel_dict.items():
	
	orig = ps['orig']
	print(f'returned {tag}:{name} to {orig}')
	put_complete(ps, orig, verbose=False)


atf_db.host_disconnect()  # Close socket

print(metadata)

