#-------------------------------------------------------------------------------

#     \  |  /
#      \ | /                                              /|     ____
#       \|/        Accelerator Test Facility             / |     |
#     ---*----------------------------------------------/------------------
#       /|\     Brookhaven National Laboratory         /   |  |  |
#      / | \   Brookhaven Science Associates, LLC          |  |
#     /  |  \                                                 |

#-------------------------------------------------------------------------------

#  atf_db_py3.py

#  Python module to support network socket communications to an ATF database
#  using Python3.x

#  Typically, one can use: import atf_db_py3 as atf_db.
 
#-------------------------------------------------------------------------------

#  Revision history

#  Wed 13 Jul 2022 04:16:20 PM EDT -- MGF
#  commented text output in get_integer function to avoid extra output in execution

#  Mon Jul 26 14:03:39 EDT 2021 -- RGM
#  Found more locations where P2-P3 string problems.

#  Mon Jul 26 13:07:27 EDT 2021 -- RGM
#  Corrected problem handling string parameters for PUTxx functions.
#  This is a Python 2 to Python 3 gotcha.

#  Wed Jul 21 16:09:45 EDT 2021 -- RGM
#  Improved some comments to make things a little more understandable.

#  Sat May  1 23:23:05 EDT 2021 -- RGM
#  This is a copy of the original atf_db upated for Python 3.x.
#  There have been no updates to the protocl itself, only how Python
#  handles strings in 3.x: Socket messages now have to be read/written
#  as byte strings (i.e., use encode/decode)

#  Fri Jul 27 16:54:45 EDT 2018 -- RGM
#  Corrected minor typos in comments.
#  No technical changes.

#  Sun Nov 19 02:28:48 EST 2017 -- RGM
#  Fixed some comments.
#  Fixed put_binary.

#  Mon Oct 23 14:29:30 EDT 2017 -- RGM
#  Moved to its own directory in /DbSockets/Python

#  Thu Oct 19 12:55:47 EDT 2017 -- RGM
#  Corrected minor typo introduced in earlier updates today.

#  Thu Oct 19 12:46:41 EDT 2017 -- RGM
#  Improved error messages, status, etc.
#  No substantive technical changes.

#  Wed Apr 19 21:19:30 EDT 2017 -- RGM
#  Initial release of new version.

#===============================================================================

from __future__ import print_function

import datetime  #  for datetime.datetime( )
import socket    #  for socket create, read, write, etc.
import string    #  for str( )
import sys       #  for exit
import time      #  for time delay, using sleep( )
import traceback #  for traceback of function calls

#-------------------------------------------------------------------------------

#  Constants

ATF_DB_HOST_DEFAULT = "portland.atf.bnl.gov"
ATF_DB_PORT_DETAULT = 1505

ATF_DB_RECEIVE_BUFFER_SIZE = 5120
ATF_DB_SEND_BUFFER_SIZE    = 5120

#  Message prefixes

ATF_DB_DEBUG   = "ATF DB - DEBUG: "
ATF_DB_ERROR   = "ATF DB - ERROR: "
ATF_DB_NOTE    = "ATF DB - NOTE: "
ATF_DB_SUCCESS = "ATF DB - SUCCESS: "
ATF_DB_WARNING = "ATF DB - WARNING: "

#-------------------------------------------------------------------------------

#  Get get binary scalar

def get_binary( channel_index = None ):

  error_message = ATF_DB_ERROR + "Problem getting binary scalar"

  if ( channel_index == None ):
    timestamp( )
    print ( error_message )
    print( ATF_DB_ERROR + "Channel index is 'None'" )
    return None

  #-----
  #  Write request

  request = "GETBS " + "'X' " + str( channel_index )

  status = socket_write( request )
  if ( status == None ):
    return None

  #-----
  #  Read reply

  reply = socket_read( ).decode( )
  split_reply = reply.split( )

  if ( split_reply[ 0 ] == "GETFAIL" ):
    timestamp( )
    print( error_message )
    print( ATF_DB_ERROR + "Channel index:", channel_index )
    return None
  else:
    return split_reply[ -1 ]

#-------------------------------------------------------------------------------

def get_channel_index( channel_name = None ):

  general_message = ATF_DB_ERROR + 'Problem finding database channel index'

  if ( channel_name == None ):
    timestamp( )
    print( general_message )
    print( ATF_DB_ERROR + "Passed a 'None' channel name" )
    atf_db_traceback( )
    return None

  #-----
  #  Write request

  status = socket_write( "GETCHIDX " + "'X' " + "'" + channel_name + "'" )
  if ( status == None ):
    return None

  #-----
  #  Read reply

  reply = socket_read( ).decode( )
  split_reply = reply.split( )

  if ( split_reply[ 0 ] == "CHIDXERR" ):
    timestamp( )
    print( general_message )
    print( ATF_DB_ERROR + "Channel name:", channel_name )
  else:
    return split_reply[ -1 ]

#-------------------------------------------------------------------------------

#  Get integer scalar

def get_integer( channel_index = None ):

  error_message = ATF_DB_ERROR + "Problem getting integer scalar"

  if ( channel_index == None ):
    timestamp( )
    print ( error_message )
    print( ATF_DB_ERROR + "Channel index is 'None'" )
    return None

  #-----
  #  Write request

  request = "GETIS " + " 'X' " + str(channel_index)

  status = socket_write( request )
  if ( status == None ):
    return None

  #-----
  #  Read reply

  reply = socket_read( ).decode( )
  split_reply = reply.split( )

  if ( split_reply[ 0 ] == "GETFAIL" ):
    timestamp( )
    print( error_message )
    print( ATF_DB_ERROR + "Channel index:", channel_index )
    return None
  else:
#    print ('The grabbed int = ', split_reply[ -1 ] )    # MGF commented this string on Wed 13 Jul 2022 04:15:55 PM EDT 
    return int( split_reply[ -1 ] )

#-------------------------------------------------------------------------------

#  Get real scalar

def get_real( channel_index = None ):

  error_message = ATF_DB_ERROR + "Problem getting real scalar"

  if ( channel_index == None ):
    timestamp( )
    print ( error_message )
    print( ATF_DB_ERROR + "Channel index is 'None'" )
    return None

  #-----
  #  Write request

  message = "GETRS " + "'X' " + str( channel_index )

  status = socket_write( message )
  if ( status == None ):
    return None

  #-----
  #  Read reply

  reply = socket_read( ).decode( )
  split_reply = reply.split( )

  if ( split_reply[ 0 ] == "GETFAIL" ):
    timestamp( )
    print( error_message )
    print( ATF_DB_ERROR + "Channel index:", channel_index )
    return None
  else:
    return float( split_reply[ -1 ] )

#-------------------------------------------------------------------------------

#  Get character string scalar

def get_string( channel_index = None ):

  error_message = ATF_DB_ERROR + "Problem getting character string scalar"

  if ( channel_index == None ):
    timestamp( )
    print ( error_message )
    print( ATF_DB_ERROR + "Channel index is 'None'" )
    return None

  #-----
  #  Write request

  request = "GETCS " + "'X' " + str( channel_index )

  status = socket_write( request )
  if ( status == None ):
    return None

  #-----
  #  Read reply

  reply = socket_read( ).decode( )
  split_reply = reply.split( )

  if ( split_reply[ 0 ] == "GETFAIL" ):
    timestamp( )
    print( error_message )
    print( ATF_DB_ERROR + "Channel index:", channel_index )
    return None
  else:
    return split_reply[ -1 ]

#-------------------------------------------------------------------------------

#  Connect to database host

def host_connect( host_name = None, port_number = None ):

  global atf_db_socket

  #----------
  #  Check for unexpected arguments

  if ( host_name == None ):
    timestamp( )
    print( ATF_DB_ERROR + "Database host name = 'None'" )
    atf_db_traceback( )
    return None

  if ( port_number == None ):
    timestamp( )
    print( ATF_DB_ERROR + "Database port number = 'None'" )
    atf_db_traceback( )
    return None

  #----------
  #  Print message that we are trying to connect

  timestamp( )

  print( "[This module is to be imported from Pyton 3.x scripts.]" )

  print( ATF_DB_NOTE + "Connecting to database host", host_name,
         "on port", port_number, "..." )

  #----------
  #  Create socket

  try:
    atf_db_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
  except:
    timestamp( )
    print( ATF_DB_ERROR + "Problem creating socket" )
    atf_db_traceback( )
    return None

  #----------
  #  Allow port to be reused immediately without any waiting

  try:
    atf_db_socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
  except:
    timestamp( )
    print( ATF_DB_ERROR + "Problem setting socket option: SO_REUSEADDR" )
    return None

  #----------
  #  Turn on keepalive

  try:
    atf_db_socket.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1 )
  except:
    timestamp( )
    print( ATF_DB_ERROR + "Problem setting socket option: SO_KEEPALIVE" )
    return None

  #----------
  #  Disable Nagle's algorithm

  try:
    atf_db_socket.setsockopt( socket.IPPROTO_TCP, socket.TCP_NODELAY, 1 )
  except:
    timestamp( )
    print( ATF_DB_ERROR + "Problem setting socket option: TCP_NODELAY" )
    return None

  #----------
  #  Connect to ATF host

  try:
    atf_db_socket.connect( (host_name, port_number) )     #  expects tuple
  except:
    timestamp( )
    print( ATF_DB_ERROR + "Problem connecting to database host" )
    print( ATF_DB_ERROR + "Host: ", host_name )
    print( ATF_DB_ERROR + "Port: ", port_number )
    return None

  try:
    connection_banner = socket_read( )
  except:
    timestamp( )
    print( ATF_DB_ERROR + "Problem reading database host connection banner" )
    return None

  timestamp( )
  print( ATF_DB_SUCCESS + "Successful connection to database host." )
  #print( "Banner:", repr( connection_banner ) )  #  see \r,\n,\0
  #print( "Banner:", connection_banner.strip('\r\n\0') )

#-------------------------------------------------------------------------------

#  Put binary scalar

def put_binary( channel_index = None, value = None ):

  error_message = ATF_DB_ERROR + "Problem writing binary scalar to database"

  if ( channel_index == None ):
    timestamp( )
    print ( error_message )
    print( ATF_DB_ERROR + "Channel index is 'None'" )
    return None

  if ( value == None ):
    timestamp( )
    print( error_message )
    print( ATF_DB_ERROR + "Binary value is 'None'" )
    return None

  #-----
  #  Write request

  request = "PUTBS " + "'X' " + "'ACK' " + str(channel_index) + \
            " '" + value + "'"

  status = socket_write ( request )

  if ( status == None ):
    return None

  #-----
  #  Read reply

  reply = socket_read( ).decode( )
  split_reply = reply.split( )

  if ( split_reply[ 0 ] != "PUTOK" ):
    timestamp( )
    print( error_message )
    print( ATF_DB_ERROR + "Channel index:", channel_index )
    print( ATF_DB_ERROR + "Binary value:", value )
    return None

#-------------------------------------------------------------------------------

#  Write integer scalar to database

def put_integer( channel_index = None, value = None ):

  error_message = "Problem writing integer scalar to database"

  if ( channel_index == None ):
    timestamp( )
    print( ATF_DB_ERROR + error_message )
    print( ATF_DB_ERROR + "Channel index is 'None'" )
    return None

  if ( value == None ):
    timestamp( )
    print( ATF_DB_ERROR + error_message )
    print( ATF_DB_ERROR + "Integer scalar is 'None'" )
    return None

  request = "PUTIS " + "'X' " + "'ACK' " + str(channel_index) + " " + str(value)
  socket_write( request )

  reply = socket_read( ).decode( )
  split_reply = reply.split( )

  if split_reply[ 0 ] != "PUTOK":
    print( ATF_DB_ERROR + error_message )
    return None
  else:
    return 0

#-------------------------------------------------------------------------------

#  Write real scalar to database

def put_real( channel_index = None, value = None ):

  error_message = "Problem writing real scalar to database"

  if ( channel_index == None ):
    timestamp( )
    print( ATF_DB_ERROR + error_message )
    print( ATF_DB_ERROR + "Channel index is 'None'" )
    return None

  if ( value == None ):
    timestamp( )
    print( ATF_DB_ERROR + error_message )
    print( ATF_DB_ERROR + "Real scalar is 'None'" )
    return None

  request = "PUTRS " + "'X' " + "'ACK' " + str(channel_index) + " "+ str(value)

  socket_write( request )

  reply = socket_read( ).decode( )
  split_reply = reply.split( )

  if split_reply[ 0 ] != "PUTOK":
    print( ATF_DB_ERROR + error_message )
    return None
  else:
    return 0

#-------------------------------------------------------------------------------

#  Write character string scalar to database

def put_string( channel_index = None, value = None ):

  error_message = "Problem writing character string scalar to database"

  if ( channel_index == None ):
    timestamp( )
    print( ATF_DB_ERROR + error_message )
    print( ATF_DB_ERROR + "Channel index is 'None'" )
    return None

  if ( value == None ):
    timestamp( )
    print( ATF_DB_ERROR + error_message )
    print( ATF_DB_ERROR + "Character string scalar is 'None'" )
    return None

  request = "PUTCS " + "'X' " + "'ACK' " + \
            str(channel_index) + " '"  + value + "'"

  socket_write( request )

  reply = socket_read( ).decode( )
  split_reply = reply.split( )

  if split_reply[ 0 ] != "PUTOK":
    print( ATF_DB_ERROR + error_message )
    return None
  else:
    return 0

#-------------------------------------------------------------------------------

def host_disconnect( ):

  try:
    atf_db_socket.shutdown( 0 )
    atf_db_socket.close( )
    timestamp( )
    print( ATF_DB_NOTE + "Socket closed" )
    return None
  except:
    timestamp( )
    print( ATF_DB_ERROR + "Problem closing ATF database socket" )
    return None

#-------------------------------------------------------------------------------

def sleep( sleep_time = None ):

  if ( sleep_time == None ):
    timestamp( )
    print( ATF_DB_ERROR + "Sleep time specified as 'None'" )
    return None

  try:
    time.sleep( sleep_time )
  except KeyboardInterrupt:
    print( ATF_DB_WARNING +"Sleep terminated by keyboard interrupt" )
    sys.exit( )
  except:
    timestamp( )
    print( ATF_DB_ERROR + "sleep() returned error" )
    return None

  return 0

#-------------------------------------------------------------------------------

def socket_read( ):

  global atf_db_socket

  try:
    message = atf_db_socket.recv( ATF_DB_RECEIVE_BUFFER_SIZE )
  except:
    timestamp( )
    print( ATF_DB_ERROR + "Problem reading from socket" )
    return None

  return message

#-------------------------------------------------------------------------------

def socket_write( message = None ):

  global atf_db_socket

  error_message = ATF_DB_ERROR + "Problem writing to database socket"

  if ( message == None ):
    timestamp( )
    print( error_message )
    print( ATF_DB_ERROR + "Message is 'None'")
    return None

  terminated_message = message.encode() + "\n".encode()
  #print( "DEBUG - About to write:", repr( terminated_message ))

  try:
    atf_db_socket.sendall( terminated_message )
  except:
    timestamp( )
    print( error_message )
    print( ATF_DB_ERROR + "Trying to write the following:")
    print( repr( terminated_message ) )
    return None

  return 0

#-------------------------------------------------------------------------------

def timestamp( ):
  print( '-' * 26 )
  print( str( datetime.datetime.now() ) )

#-------------------------------------------------------------------------------

#def traceback( ):
#  print ( "ATF DB - Traceback follows:" )
#  print ( "A traceback would be here" )
#  #traceback.print_stack()

#-------------------------------------------------------------------------------

