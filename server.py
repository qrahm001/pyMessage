import socket
import sys
import time
import datetime

class Message:
        def __init__(self, msg, from_p, to_p, ts):
                self.content = msg
                self.sender = from_p
                self.receiver = to_p
                self.timeStamp = ts
        def get_sender(self):
                return self.sender
        def get_content(self):
                return self.content
        def get_receiver(self):
                return self.receiver

class Profile:
        def __init__(self, user):
                self.name = user
                self.messages = []
        def msg_cnt(self):
                return str(len(self.messages))
        def get_msgs(self):
                return self.messages
        def get_name(self):
                return self.name
        def send_msg(self, msg):
                self.messages.append(msg)
        def del_msgs(self):
                self.messages[:] = []
        
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created')
except socket.error:
    print('Failed to create socket.')
    sys.exit()
 
 
# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error:
    print ('Bind failed')
    sys.exit()
     
print ('Socket bind complete')

#current users and their data
users = ['Bill', 'Bob', 'Bu', 'Salululul']
profiles = []
passwords = ['B1ll', 'B0b', 'B4', 'Saulty']

#init all the profiles
for member in users:
        temp = Profile(member)
        profiles.append(temp)
        temp = None

#print 'Profiles: ' + str(len(profiles))

menu = '\n [0] Change Password \n [1] Logout \n [2] Messages \n [3] Refresh \n'
msg_menu = '\n [1] View Unread Messages \n [2] Send Message \n [3] Broadcast Message \n [4] Exit \n'

#current sessions
clients = []
clients_port = []
account = [] #stores the index of user associated with each client
 
#now keep talking with the client
while 1:
    # receive data from client (data, addr)
    d = s.recvfrom(1024)
    data = d[0]
    addr = d[1]

    #if packet is empty, go back into rcv state
    if not data:
                break

    #if new client, add into clients list
    if (addr[0] not in clients):
                clients.append(addr[0])
                clients_port.append(addr[1])
                account.append(-1)

    #parse received packet for id, and msg
    rcv_id = data[0:1]
    rcv_msg = data[1:]
    
    #Server asks for username
    if (rcv_id == '0'):
                packet_id = '1'
                packet_msg = 'Enter Your Username: '
                packet = packet_id + packet_msg 

                s.sendto(packet, addr)
                continue

    #login
    if (rcv_id == '1'):
                #check if username is valid
                user = rcv_msg
                if (user not in users):
                        packet_id = '1'
                        packet_msg = 'Incorrect Username, Please Re-enter: '

                elif (users.index(user) in account):
                        packet_id = '1'
                        packet_msg = 'Account is Currently Being Used \nTry a Different Account!'
                
                else: 
                        #links client, with requested account
                        client_ind = clients.index(addr[0])
                        user_ind = users.index(user)
                        account[client_ind] =  user_ind

                        #server asks for password for requested account
                        packet_id = '2'
                        packet_msg = 'Enter Your Password: '
                
                packet = packet_id + packet_msg

                s.sendto(packet, addr)
                continue

    #server gives client menu of options
    if (rcv_id == '2'):
                #check if password matches the username
                password = rcv_msg

                clients_ind = clients.index(addr[0])
                curr_account = account[clients_ind]

                if (password != passwords[curr_account]):
                        packet_id = '2'
                        packet_msg = 'Incorrect Password, Please Re-Enter'
                        
                else:
                        packet_id = '3'
                        curr_prof = profiles[curr_account]
                        no_msg = str(curr_prof.msg_cnt())
                        packet_msg = 'Succesful Login! \n' + no_msg + ' New Messages \n'  + menu

                packet = packet_id + packet_msg
                s.sendto(packet, addr)
                continue

    if (rcv_id == '3'):
                #check which option the user selected
                option = rcv_msg

                if (option == '0'):
                        packet_id = '5'
                        packet_msg = 'Enter Old Password: '
                        

                elif (option == '1'):
                        client_ind = clients.index(addr[0])
                        del clients[client_ind]
                        del clients_port[client_ind]
                        del account[client_ind]

                        packet_id = '4'
                        packet_msg = 'Logout Succesful! \n'

                elif (option == '2'):
                        packet_id = '7'
                        packet_msg = msg_menu
                elif (option == '3'):
                        packet_id = '3'
                        packet_msg = menu
                else:
                        packet_id = '3'
                        packet_msg = 'Invalid Character Entered, Please Re-Enter'
                
                packet = packet_id + packet_msg
                s.sendto(packet, addr)
                continue

    #check to see if entered password is correct
    if (rcv_id == '5'):
                old_pass = rcv_msg
                #check if old_password matches
                client_ind = clients.index(addr[0])
                curr_user = account[client_ind]
                if (passwords[curr_user] != old_pass):
                        packet_msg =  'Incorrect Password, Try Again!'
                        packet_id = '5'

                else:
                        packet_msg = 'Enter Your New Password'
                        packet_id = '6'

                packet = packet_id + packet_msg
                s.sendto(packet, addr)
                continue

                #updating the password
                if (rcv_id == '6'):
                                        new_pass = rcv_msg
                                        #update the password for this user
                                        client_id = clients.index(addr[0])
                                        curr_user = account[client_ind]
                                        passwords[curr_user] = new_pass
                                        
                                        packet_id = '3'
                                        packet_msg = 'Password Changed Successfully! \n' + menu
                                        packet = packet_id + packet_msg
                                        
                                        s.sendto(packet, addr)
                                        continue 

    #menu letting user select Messages
    if (rcv_id == '7'):
                option = rcv_msg
                if (option == '1'):
                        packet_id = '7'
                        packet_msg = '\nUnread Messages: \n' 
                        client_ind = clients.index(addr[0])
                        curr_user = account[client_ind]
                        curr_prof = profiles[curr_user]

                        if (str(curr_prof.msg_cnt()) == '0'):
                                packet_msg += ' No new unread messages! \n'

                        else:
                                #print curr_prof.get_name() + ': ' + curr_prof.msg_cnt()
                                msgs = curr_prof.get_msgs()
                                for msg in msgs:
                                        packet_msg += msg.get_sender() + ' sent: ' + msg.get_content() + ' -at- ' + datetime.datetime.fromtimestamp(msg.timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
                        
                        packet_msg += '\n Select another option!\n' + msg_menu
                        #deletes messages after they've been viewed
                        curr_prof.del_msgs()

                elif (option == '2'):
                        packet_id =  '8'
                        packet_msg = 'Enter message in Format =  Recipient name: Message'
                elif (option == '3'):
                        packet_id = '9'
                        packet_msg = 'Enter Message: '
                elif (option == '4'):
                        packet_id = '3'
                        packet_msg = menu
                else:
                        packet_id = '7'
                        packet_msg = 'Invalid Character \nPlease Re-Enter Selection \n'
                
                packet = packet_id + packet_msg
                s.sendto(packet, addr)
                continue

    #parse user entered message, and send to specified recipient
    if (rcv_id == '8'):
                user_msg = rcv_msg
                #print user_msg
                colon_ind = user_msg.find(':')

                #identify sender name
                client_ind = clients.index(addr[0])
                user_ind = account[client_ind]

                sender = users[user_ind]
                recipient = user_msg[0:colon_ind]
                msg = user_msg[colon_ind + 1:]

                if (recipient not in users):
                        packet_id = '8'
                        packet_msg = 'Invalid Recipient, Please Re-Enter Recipient and Message \n'

                #check if recipient is currently online
                elif (users.index(recipient) in account):
                        acnt_ind = account.index(users.index(recipient))
                        client_addr = clients[acnt_ind]
                        client_port = clients_port[acnt_ind]
                        
                        #sends message to live user
                        packet_id = 'r'
                        packet_msg = sender + ' sent: ' + msg
                        packet = packet_id + packet_msg
                        addr_tup = (client_addr, client_port)
                        s.sendto(packet, addr_tup)
                        temp_addr = None

                        packet_id = '7'
                        packet_msg = 'Message Sent Succesfully! \n' + msg_menu
                
                else: 
                        #create msg object
                        ts = time.time()
                        temp = Message(msg, sender, recipient, ts)
                        rec_ind = users.index(recipient)
                        #print 'Rec_index: ' + str(rec_ind)
                        profiles[rec_ind].send_msg(temp)
                        temp = None
                        
                        packet_id = '7'
                        packet_msg = 'Message Sent Succesfully! \n' + msg_menu

                packet = packet_id + packet_msg
                s.sendto(packet, addr)
                continue

    #broadcast message to all active users
    if (rcv_id == '9'):
                user_msg = rcv_msg
                packet_id = 'b'
                b_packet = packet_id + user_msg
                        
                        
                for c,p in zip(clients, clients_port):
                        #don't want to broadcast message to self
                        if (c != addr[0]):
                                s.sendto(b_packet, (c, p))

                packet_id = '7'
                packet_msg = 'Message Sent Succesfully! \n' + msg_menu
                packet = packet_id + packet_msg
                s.sendto(packet, addr)
                continue        

s.close()
