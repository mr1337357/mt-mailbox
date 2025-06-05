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

interface = None

commands = {}

def help(src,message):
    interface.sendText('Messagebox commands: help, send {addr} {message}, get {index}, del {index}',src)

commands['help'] = help

def send(src,message):
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
    
commands['send'] = send

def get(src,message):
    m = message.split()
    index = 0
    try:
        index = int(m[1])
    except:
        pass
    if not src in messages:
        messages[src] = mqueue()
    interface.sendText(messages[src].get(index),src)

commands['get'] = get

def delet(src,message):
    m = message.split()
    index = 0
    try:
        index = int(m[1])
    except:
        pass
    if not src in messages:
        messages[src] = mqueue()
    messages[src].delete(index)

commands['del'] = delet

def onMessage(src,message):
    print('{}: {}'.format(src,message))
    l = message.lower() 
    for command in commands:
        if l.startswith(command):
            commands[command](src,message)
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
            onMessage(packet['fromId'],dec['text'])
        else:
            print(id,ouraddr)
    else:
        print(dec['portnum'])


pub.subscribe(onRecv, 'meshtastic.receive')

def onLoss():
    print('onLoss')
    pass

pub.subscribe(onLoss, 'meshtastic.connection.lost')

interface = meshtastic.tcp_interface.TCPInterface(hostname = configfile['host'])

us = interface.getNode('^local')
ouraddr = hex(us.nodeNum)[2:]

while True:
    time.sleep(60)
    for mq in messages:
        mq.clean()
