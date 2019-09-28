import socket   #for sockets
import sys  #for exit
from getpass import getpass 
 
# create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
except socket.error:
    print ('Failed to create socket')
    sys.exit()
 
host = '10.0.0.4';
port = 8888;

init_connect = True;
rcv_id = '0'

while(1) :

    #send a packet to server telling it about this connection
    if (init_connect == True):
        packet_id ='0'
        packet_msg = 'Init'
        packet = packet_id + packet_msg
         
    try :
        if (rcv_id != 'r' and rcv_id != 'b'):
            #Sends the packet
            s.sendto(packet, (host, port))
            
        #receives packet
        d = s.recvfrom(1024)
        reply = d[0]
        addr = d[1]

        if not reply: #if rcved packet is empty/error
            break

        else:
            init_connect = False; #no longer initiating connection
            rcv_id = reply[0:1]
            rcv_msg = reply[1:]
            
            if (rcv_id != 'r' and rcv_id != 'b'):
                print(rcv_msg)

            #User Entering a Password
            if (rcv_id in ['2', '5', '6']):
                packet_msg = getpass()
                packet = rcv_id + packet_msg

            #User Logged Out
            elif (rcv_id == '4'):
                init_connect = True
                break   

            elif (rcv_id == 'r'):
                print('\nNEW MESSAGE: \n' + rcv_msg)
            
            elif (rcv_id == 'b'):
                print('BROADCAST: ' + rcv_msg)
            else:
                packet_msg = raw_input()
                packet = rcv_id + packet_msg
            

    except socket.error:
        print('Socket Error')
