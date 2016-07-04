#!/usr/bin/env python
# coding: utf-8
#
# This is the servent, it keeps part of the database.
# Receives requests from clients ( or from other servents ) and answers them.
# 


import re
import sys
import socket
import struct
import subprocess


servers = []
sequences = {}


def ip2int(addr):
  '''
    A utilitary function that translates an address to an int.
  '''
  return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
  '''
    A utilitary function that translates an int to an address.
  '''
  return socket.inet_ntoa(struct.pack("!I", addr)) 



def read_file(filename):
  '''
    This method reads the file with the key-value pairs.
  '''
  
  f = open(filename, 'r')
  index = 0
  dictionary = {}
  
  for line in f.readlines():
    index += 1
    splitted = line.split('#')[0]
    splitted = splitted.replace('\n', '')
    if len(splitted) == 0:
      continue
    
    splitted = [value for value in re.split(' |\t', splitted) if len(value) > 0]
    if len(splitted) < 2:
      print 'Bad formatted line: ', index, ':', filename
    else:
      key = splitted[0]
      value = splitted[1]
      for i in range(2, len(splitted)):
        value += ' ' + splitted[i]
      
      if key in dictionary:
        dictionary[key].append(value)
      else:
        dictionary[key] = [value]
  f.close()
  return dictionary



def answer_client(sock, dictionary, key, client_addr):
  '''
    This method checks if this servent contains at least a key-value pair
    the client is looking for.
  '''
  fmt_str = "!H1022s"
  print 'Answering client ', client_addr, ' ...'
  print 'Searching for:', key, '...'
  if key in dictionary:
    print 'Found!'
    for value in dictionary[key]:
      sock.sendto(struct.pack(fmt_str, 3, value), client_addr)
  print ''



def sendall_query(sock, forbidden_addr, ttl, ip, port, seq_number, key):
  '''
    This method sends a query to every neighbor but forbidden_addr.
  '''
  
  # Just send the query to other servers if the ttl is positive.
  if ttl <= 0:
    return
  
  fmt_str = "!HHiHi1010s"
  for s in servers:
    if s != forbidden_addr:
      msg_bytes = struct.pack(fmt_str, 2, ttl, ip2int(ip), port, seq_number, key)
      sock.sendto(msg_bytes, s)



def process_query(sock, dictionary, msg_bytes, addr):
  fmt_str = "!HHiHi1010s"
  fields_list = struct.unpack(fmt_str, msg_bytes)
  
  ttl = int(fields_list[1])
  ip = int2ip(fields_list[2])
  port = int(fields_list[3])
  seq_number = int(fields_list[4])
  key = fields_list[5].replace('\x00', '')
  if ttl > 0:
    answer_client(sock, dictionary, key, (ip, port))
    client_addr = (ip, port)
    if not(client_addr in sequences and sequences[client_addr] > seq_number):
      sequences[client_addr] = seq_number
      sendall_query(sock, addr, ttl-1, ip, port, seq_number, key)
  



def process_clireq(sock, dictionary, msg_bytes, addr):
  fmt_str = "!H1022s"
  key = struct.unpack(fmt_str, msg_bytes)[1].replace('\x00', '')
  answer_client(sock, dictionary, key, addr)
  
  if not (addr in sequences):
    sequences[addr] = 0
  else:
    sequences[addr] += 1
  
  sendall_query(sock, ('', 0), 3, addr[0], addr[1], sequences[addr], key)



def process_package(sock, dictionary, msg_bytes, addr):
  '''
    Detects the type of the package received, and calls the correct
    function to process it.
  '''
  fmt_str = '!H1022s'
  
  fields_list = struct.unpack(fmt_str, msg_bytes)
  
  if fields_list[0] == 1:
    #CLIREQ
    process_clireq(sock, dictionary, msg_bytes, addr)
  elif fields_list[0] == 2:
    # QUERY
    process_query(sock, dictionary, msg_bytes, addr)



def main():
  if len(sys.argv) < 4 or len(sys.argv) > 13:
    print 'Invalid Arguments'
    sys.stdout.write('Usage: python ' + sys.argv[0] + ' [port]' + ' [filename]')
    print ' [ip-servent1:port-servent1] [ip-servent2:port-servent2] ... [ip-servent10:port-servent10]'
    return
  
  print 'Starting...'
  dictionary = read_file(sys.argv[2])
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  
  # Binding the socket to a tuple (ip, port).

  hostname =  socket.gethostname()
  
  shell_cmd = "ifconfig | awk '/inet addr/{print substr($2,6)}'"
  proc = subprocess.Popen([shell_cmd], stdout=subprocess.PIPE, shell=True)
  (out, err) = proc.communicate()
  
  ip_addresses = out.split('\n')
  ip = ip_addresses[0]
  for x in xrange(0, len(ip_addresses)):
    try:
      if ip_addresses[x][:5] != "127.0" and ip_addresses[x].split(".")[3] != "1":
        ip = ip_addresses[x]
    except:
      pass
  
  print 'Running at: ', ip, int(sys.argv[1])
  sock.bind((ip, int(sys.argv[1])))
  
  
  # Adding the neighbors to a list of servers.
  for i in range(3, len(sys.argv)):
    splitted = sys.argv[i].split(':')
    servers.append((splitted[0], int(splitted[1])))
  
  
  while True:
    try:
      (msg_bytes, addr) = sock.recvfrom(1024)
      print 'Processing package from: ', addr
      process_package(sock, dictionary, msg_bytes, addr)
    except socket.timeout:
      continue
  

if __name__ == '__main__':
  main()
