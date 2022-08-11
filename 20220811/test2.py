import atf_db_py3x as atf_db
import time

host_name = '172.16.82.101'
port_name = 1505

atf_db.host_connect(host_name,port_name)  # Generate socket

def GetPOPIN(POPN):
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
POPINLIST = [['laser_profile','gun_monument','38'],['LTR','21','6'],['LPOP1','11','2'],['HPOP1','18','4'],['HPOP2','14','75'],['CHIC_UP','36','54'],['CHIC_DOWN','36','55'],['HPOP3','13','24'],['HPOP4','12','5'],['HPOP5','38','76'],['HPOP6','39','77'],['FPOP1','1','8'],['HES','blades','9'],['FPOP2','2','10'],['FPOP3','6','58'],['FPOP4','4','16'],['GPOP6','30','23']]




def CAM2POPID(my_dict,keyname,val):
	for popn, popinparam in my_dict.items():
		if val == popinparam[keyname]:
             		return popn
 
	return "There is no such Key"

pop_in_dict = {}
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


atf_db.host_disconnect()
