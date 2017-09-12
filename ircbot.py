import os
import socket
import sys
import time
import logging

from ircgmailbackend import GMAILClient

start_time = time.time()

server = "irc.freenode.net"       #settings
channel ="#channelname"
botnick = "botname"
LOG = logging.getLogger(__name__)
connection_timeout = 0

def format_log(log_path, enable_debug):
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    LOG.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - '
                                  '%(levelname)s - %(message)s')

    # Configuring console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    LOG.addHandler(console_handler)

    # Configuring logging to file
    file_handler = logging.FileHandler(log_path+'/bot.log', mode='w+')
    file_handler.setFormatter(formatter)
    LOG.addHandler(file_handler)


def log(msg):
    LOG.debug(msg)

def retry_count(count):
    time.sleep(10)
    return count+1

def irc_login():
    global irc
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
    log("connecting to:"+server)
    irc.connect((server, 6667))                                                         #connects to the server
    log('irc connected')
    irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This is an IRC bot!\n") #user authentication
    irc.send("NICK "+ botnick +"\n")                            #sets nick
    irc.send("PRIVMSG" + " NICKSERV :identify " + "<PASSWORD>" +"\n")
    irc.send("JOIN "+ channel +"\n")        #join the chan
    log("channel joined...")

format_log('./log', True)
irc = None
irc_login()

while 1:    #puts it in a loop
   try:
       text=irc.recv(2040)  #receive the text
       log('receiving irc data: {}'.format(text))
       if not text:
           raise ValueError('Empty response')
   except:
       if connection_timeout > 10:
           log('IRC disconnected from server! No more retries left!')
           sys.exit(1)
       else:
           log('Connection disconnected. Retrying...')
           connection_timeout=retry_count(connection_timeout)
           log('Connection timeout: %s' % connection_timeout)
           irc_login()
           continue

   log('respone')
   log(text)   #print text to console

   if text.find('PING') != -1:                          #check if 'PING' is found
      irc.send('PONG ' + text.split() [1] + '\r\n') #returnes 'PONG' back to the server (prevents pinging out!)
   elif text.find('PRIVMSG') !=-1: #you can change !hi to whatever you want
       t = text.split('PRIVMSG %s' % channel) #you can change t and to :)
       frm = t[0]
       msg = t[1] #this code is for getting the first word after !hi
       elapsed_time = time.time() - start_time
       log('Elapsed time %s' % elapsed_time)
       #irc.send('PRIVMSG '+channel+' :I just sent you an email. Please check. ! \r\n')
       if elapsed_time > 300:
           test=GMAILClient()
           #test.email('xgridbot@gmail.com','baqar@xgrid.co','[IRC_BOT] New Message on IRC Channel','From: %s - Message:%s' % (str(frm),str(msg)))
           test.email('from@gmail.com','to@gmail.com','[IRC_BOT] New Message on IRC Channel','From: %s - Message:%s' % (str(frm),str(msg)))
           start_time = time.time()
       else:
           log('skipping email')
