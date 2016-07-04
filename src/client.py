#!/usr/bin/env python
# coding: utf-8
#
# This is the client, it interacts with the user, sending and receiving
# messages from the overlay network.
#


import sys
import time
import socket
import struct


def send_query_package(sock, servent_address, key):
  '''
    This function sends a query package to the servent this client knows.
  '''
  
  fmt_str = "!H1022s"
  
  if len(key) > 1000:
    print 'The key is too large, maximum size is 1000 characters.'
    return False
  
  msg_bytes = struct.pack(fmt_str, 1, key)
  sock.sendto(msg_bytes, servent_address)
  return True


def disassemble_message(msg_bytes):
  '''
    Function to disassemble a package this client received from a servent.
  '''
  
  fmt_str = "!H1022s"
  fields_list = struct.unpack(fmt_str, msg_bytes)
  return fields_list[1]

  

def main():
  if len(sys.argv) != 2:
    print 'Invalid Arguments'
    print 'Usage: python ', sys.argv[0], ' [ip-servent:port-servent]'
    return
  
  servent_address = sys.argv[1].split(':')
  servent_address = (servent_address[0], int(servent_address[1]))
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.settimeout(4)
  
  while True:
    sys.stdout.write('Key: ')
    
    # Keep the number of timeouts already happened.
    tries=0
    
    # If the package was sent correctly, prints the responses until
    # the socket timeouts.
    if send_query_package(sock, servent_address, raw_input()):
      while True:
        try:
          (msg_bytes, addr) = sock.recvfrom(1024)
          print addr, " ", disassemble_message(msg_bytes)
        except socket.timeout:
          print 'Timeout ...'
          tries+=1
          if tries==2:
            break
    print ''
  
    

if __name__ == '__main__':
  main()
