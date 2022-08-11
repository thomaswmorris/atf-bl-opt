import atf_db_py3x as atf_db
import time
from datetime import date
import pandas as pd

host_name = '172.16.82.101'
port_name = 1505

atf_db.host_connect(host_name,port_name)  # Generate socket

def ReadFG_first_time_return_statchix(fgN):
   fgname = "FRAME" + str(fgN) + "_DB::FGR" + str(fgN) + ";"
   xposchix = atf_db.get_channel_index(fgname+"RCX;CENTROID_X")
   xpos = atf_db.get_real(xposchix)
   yposchix = atf_db.get_channel_index(fgname+"RCY;CENTROID_Y")
   ypos = atf_db.get_real(yposchix)
   xsigchix = atf_db.get_channel_index(fgname+"RSX;SIGMA_X")
   xsig = atf_db.get_real(xsigchix)
   ysigchix = atf_db.get_channel_index(fgname+"RSY;SIGMA_Y")
   ysig = atf_db.get_real(ysigchix)
   pixsumchix = atf_db.get_channel_index(fgname +"RM00;SUM_PIXELS")
   pixsum = atf_db.get_real(pixsumchix)
   return [xposchix,yposchix,xsigchix,ysigchix,pixsumchix]


def GetPOPIN(POPN):
	if POPN == 'None' : return "'INSERT'"
	return atf_db.get_binary(atf_db.get_channel_index("RT_DATABASE::POPCTL" + POPN + ";RPU;RDBK_REQ_POP_UP_CKT_"+ POPN))

def PSCurrentReadSet(ChannelName,db=''):
	return atf_db.get_real(atf_db.get_channel_index(f'{db}::' + str(ChannelName) + ";CDS;SET_CURRENT_SETPT"))

def FG_connected_to(FGn):
	return atf_db.get_integer(atf_db.get_channel_index("RT_DATABASE::VID_SWITCH;CMM;VID_MON_0"+str(FGn)+"_MUX"))

Channel_name = 'DARL31' 
timestamp1 = float(time.time())
print( "Channel "+ Channel_name + " set point is:",PSCurrentReadSet(Channel_name,'RT_DATABASE') )
timestamp2 = float(time.time())
print("delta time = ", timestamp2 - timestamp1)


# POPINLIST = [POPIN_NAME, POIPIN_#, POPIN_CAM_#],[]]
POPINLIST = [['laser_profile','None','38'],['LTR','21','6'],['LPOP1','11','2'],['HPOP1','18','4'],['HPOP2','14','75'],['CHIC_UP','36','54'],['CHIC_DOWN','36','55'],['HPOP3','13','24'],['HPOP4','12','5'],['HPOP5','38','76'],['HPOP6','39','77'],['FPOP1','1','8'],['HES','None','9'],['FPOP2','2','10'],['FPOP3','6','58'],['FPOP4','4','16'],['GPOP6','30','23']]


pop_in_dict = {}

def CAM2POPID(my_dict,keyname,val):
	for popn, popinparam in my_dict.items():
		if val == popinparam[keyname]:
             		return popn


for name, n_pop, n_cam in POPINLIST:

	pop_in_dict[name] = {}
	pop_in_dict[name]['n_pop'] = n_pop
	pop_in_dict[name]['n_cam'] = n_cam
	stat = GetPOPIN(n_pop)
	pop_in_dict[name]['status'] = stat
	print(f'POP-IN: {name} status is {stat}')

CAMN = 77
POPNAME = CAM2POPID(pop_in_dict,'n_cam',str(CAMN))

print(f' POPIN on CAM={CAMN} is {POPNAME} ')

Frame_Grabber_list = ['FG1','FG2','FG3','FG4','FG5','FG6','FG7','FG8']

fg_in_dict = {}

for tag in Frame_Grabber_list:

	fg_in_dict[tag] = {}
	stat = FG_connected_to(tag[-1])
	fg_in_dict[tag]['n_cam'] = stat
	POPNAME = CAM2POPID(pop_in_dict,'n_cam',str(stat))
	print(f'Frame grabber: {tag} connected to CAM {stat} on POP-IN: {POPNAME}')


PS_H_line = {  "LT1HX" : "CAEN3",
	       "LT1VX" : "CAEN2",
	       "LT2HX" : "CAEN1",
	       "LT2VX" : "CAEN4",
	        "TK1H" : "CAEN13",
	        "TK1V" : "CAEN14",
	        "TK2H" : "CAEN15", 
	        "TK2V" : "CAEN16",
 	        "TK3H" : "CAEN17",
	        "TK3V" : "CAEN18",
               "HT1HX" : "DARL1",
	       "HT1VX" : "DARL2",
	       "HT2HX" : "DARL3",
	       "HT2VX" : "DARL4",
		 "HQ1" : "DARL149",
		 "HQ2" : "DARL150",
		 "HQ3" : "DARL151",
               "HT3HX" : "DARL9",
	       "HT3VX" : "DARL10",
	       "HT4HX" : "DARL27",
	       "HT4VX" : "DARL28",
		 "HQ4" : "DARL152",
		 "HQ5" : "DARL153",
		 "HQ6" : "DARL154",
	       "HT3HX" : "DARL29",
	       "HT3VX" : "DARL30",
	       "HT4HX" : "DARL31",
	       "HT4VX" : "DARL32",
		 "HQ4" : "DARL155",
		 "HQ5" : "DARL156",
		 "HQ6" : "DARL157"}

channel_dict = {}
timestamp1 = float(time.time())
for tag, name in PS_H_line.items():	

	channel_dict[tag] = {}
	channel_dict[tag]['name']  = name
	if name[:4] == 'CAEN': 
		channel_dict[tag]['db'] = 'CAEN_DB'
		
	else: 
		channel_dict[tag]['db'] = 'RT_DATABASE'

	if name[:4] == 'PTEN':
		channel_dict[tag]['tol'] = 1e1
	if name[:4] == 'DARL':
		channel_dict[tag]['tol'] = 1e-1		

	channel_dict[tag]['orig'] = PSCurrentReadSet(name, channel_dict[tag]['db']) 

#	print(tag, name)
timestamp2 = float(time.time())

for tag, ps in channel_dict.items():
	
	orig = ps['orig']
	print(f'H_line PS {tag}:{ps["name"]} set is {orig}')

print("delta time = ", timestamp2 - timestamp1)



logtimestamp = int(time.time())
metadata = pd.DataFrame(columns=['logtimestamp', *channel_dict, *pop_in_dict, *fg_in_dict] )
print(metadata.columns)


atf_db.host_disconnect()

filenametimestamp = str(date.today())

print(filenametimestamp)

scan_id = len(metadata)
#metadata.loc[scan_id, ['logtimestamp', *channel_dict]] = time.time(),*[PSCurrentReadSet(channel_dict['name'], channel_dict['db']) for channel_dict in channel_dict.values()]
#metadata.loc[scan_id, [f'{POP}_{col}' for col in POP_cols]] = *ReadFG(fgN), filename




metadata.to_csv(f'{filenametimestamp}.csv')

