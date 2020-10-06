#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 14:13:22 2020

@author: alberttenigin
"""

import socket
import os

def read_address():    
    dir = os.path.dirname(os.path.abspath(__file__))
    try:
        f = open(dir + '/config.txt','r')
    except FileNotFoundError:
        print('cannot find config!')
        return
    else:
        print('config file is located')
    try:
        contents = f.readlines()
    except SyntaxError:
        print('config file reading error!')
        return
    else:
        print('reading config is ok')
    f.close()
    
    return(contents[1], int(contents[2]))

def connect_socket():
    host, port = read_address()

    sock = socket.socket()
    sock.connect((host, port))
    
    return sock

def send_message(message, sock):
    sock.send(message.encode())