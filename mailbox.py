import sys
import time
from pubsub import pub

import meshtastic
import meshtastic.tcp_interface

from ini import ini
from mqueue import mqueue

ouraddr = '00000000'

configfile = ini('config.cfg')

messages = {}

public = mqueue()

interface = None

commands = {}

def help(src,message):
    m = message.split()
    try:
        return commands[m[1].lower()](src,message,True)
    except:
        return 'Messagebox commands: help, info, post {message}, read {index}, send {addr} {message}, get {index}, del {index}'

def info(src,message,help=False):
    if help:
        return 'lists available messages'
        return
    if not src in messages:
        messages[src] = mqueue()
    pub = len(public)
    priv = len(messages[src])
    return 'there are {} bulletins and {} messages'.format(pub,priv)

def post(src,message,help=False):
    if help:
        return 'post a message to the public mailbox'
        return
    msg = message[4:].strip()
    public.send(src,0,msg)
    return None

def read(src,message,help=False):
    if help:
        return 'read a message from the public mailbox'
    m = message.split()
    try:
        index = int(m[1])
        1 / index
        return public.get(index)
    except:
        return 'couldn\'t find message'

def send(src,message,help=False):
    if help:
        return 'send a private message'
    m = message.split()
    cmd = m[0]
    dest = m[1]
    payload = ' '.join(m[2:])
    print(cmd,dest,payload)
    if not dest.startswith('!'):
        dest = '!' + dest
    if not dest in messages:
        messages[dest] = mqueue()
    messages[dest].send(src,0,payload)
    


def get(src,message,help=False):
    if help:
        return 'read a private message'
    m = message.split()
    index = 0
    try:
        index = int(m[1])
    except:
        pass
    if not src in messages:
        messages[src] = mqueue()
    return messages[src].get(index)



def delet(src,message,help=False):
    if help:
        return 'delete a private message'
    m = message.split()
    index = 0
    try:
        index = int(m[1])
    except:
        pass
    if not src in messages:
        messages[src] = mqueue()
    messages[src].delete(index)

commands['help'] = help
commands['info'] = info
commands['post'] = post
commands['read'] = read
commands['send'] = send
commands['get'] = get
commands['del'] = delet

def onMessage(packet,message):
    src = packet['fromId']
    print('{}: {}'.format(src,message))
    l = message.lower() 
    for command in commands:
        if l.startswith(command):
            msg = commands[command](src,message)
            try:
                1 / len(msg)
                interface.sendText(msg,src)
            except:
                pass
            return
    interface.sendText('unknown command (try help)',src)


def onRecv(packet,interface):
    dec = None
    try:
        dec = packet['decoded']
    except:
        return
    #print(dec)
    if dec['portnum'] == 'TEXT_MESSAGE_APP':
        id = packet['toId'][1:]
        if id == ouraddr:
            onMessage(packet,dec['text'])
        else:
            print(id,ouraddr)
    else:
        print(dec['portnum'])


pub.subscribe(onRecv, 'meshtastic.receive')

def onLoss(interface):
    print('onLoss')
    globals()['interface'] = None
    while globals()['interface'] == None:
        try:
            globals()['interface'] = meshtastic.tcp_interface.TCPInterface(hostname = configfile['host'])
        except:
            print('failed to open')
            time.sleep(1)

pub.subscribe(onLoss, 'meshtastic.connection.lost')

interface = meshtastic.tcp_interface.TCPInterface(hostname = configfile['host'])

us = interface.getNode('^local')
ouraddr = hex(us.nodeNum)[2:]

while True:
    time.sleep(60)
    for mq in messages:
        messages[mq].clean()
    public.clean()
