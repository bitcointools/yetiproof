#!/usr/bin/env python

PROG = 'yetiproof'
VERSION = '0.02' 
#####################################################################
# change this value for bitcoin payment amount
PAYTO_AMOUNT_BTC = 0.0001 # min = 0.00005430 BTC
######################################################################

ELECTRUM_BIN = 'electrum'
LOGFILE_NAME = './'+PROG+'.log'

SATOSHI_PER_BTC = 100000000.0

# yetiproof 
# =========
#
# Program for time stamping of files on the Bitcoin blockchain.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import datetime
import subprocess

import urllib2
import argparse
import json

import imp
# not in the standard library
try:
 imp.find_module('bitcoin')
except ImportError:
 print 'bitcoin python library missing, please install it by: \'sudo pip install bitcoin\''
 sys.exit(-1)
import bitcoin
 
description_text = '\
Command line time stamping on the bitcoin blockchain. A hash is generated for given files, a bitcoin address is generated from the hash and a small amount of BTC is transmitted to that address as proof of existence.'

parser = argparse.ArgumentParser(description=description_text)

parser.add_argument('--version', action='version', version=PROG+' '+VERSION)

parser.add_argument('-q','--quiet', action='store_true', default=False, dest='quiet', help='Quiet mode')
parser.add_argument('-f','--file',action='append', dest='files_to_stamp', default=[],required=True,help='File(s) to be stamped on the bitcoin blockchain, allows multiple files, each file must be preceded with -f')
parser.add_argument('--burn', action='store_true', default=False, dest='burn', help='burn mode, funds are lost forever!, default: non-burn')
parser.add_argument('--stamp', action='store_true', default=False, dest='stamp', help='Stamp file(s) on the blockchain, default: regenerate hash and bitcoin (private key and) address (proof)')
parser.add_argument('--yes', action='store_true', default=False, dest='yes', help='Do not ask before sending funds, default: do ask')
parser.add_argument('--wallet', action='store', dest='wallet_file', help='/path/to/wallet/file (required with -s|--stamp)')
parser.add_argument('--passwd', action='store', dest='wallet_password', help='Wallet password (optional, will be prompted, if not given)')
parser.add_argument('--nozip', action='store_true', default=False, dest='nozipfiles', help='Do not archive file(s) into zip file, default: create zip archive')

cmdln = parser.parse_args()

files_to_stamp = cmdln.files_to_stamp

burn   = cmdln.burn
stamp  = cmdln.stamp
yes  = cmdln.yes
quiet = cmdln.quiet
zipfiles = not cmdln.nozipfiles
electrum_wallet_file = cmdln.wallet_file
electrum_wallet_password = cmdln.wallet_password

if stamp:
 if not electrum_wallet_file:
  print "Error: Wallet file is not given (Bitcoin funds needed)"
  sys.exit(-1)

text  = PROG+' '+VERSION+'\n'

if not quiet:
 sys.stdout.write(text)

if stamp:
 logfile = open(LOGFILE_NAME, 'w+')
 logfile.write(text)


for each_file in files_to_stamp:
 if os.path.exists(each_file) == 0:
  print 'Error: file '+ each_file +' does not exist'
  sys.exit(-1)

if electrum_wallet_file:
 if os.path.exists(electrum_wallet_file) == 0:
  print 'Error: electrum wallet file does not exist'
  sys.exit(-1)

#start electrum daemon if not started
p = subprocess.Popen([ELECTRUM_BIN,'daemon','status'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if p.wait() != 0:
 if not quiet:
  print 'Starting electrum ...'
  p = subprocess.Popen([ELECTRUM_BIN,'daemon','start'])
  if p.wait() != 0:
   print 'Error: electrum daemon not started...'
   sys.exit(-1)

text = 'File(s) to be hashed by sha256*:\n'

bytes = 0
data = ''
for each_file in files_to_stamp:

# binary read option to make it platform independent
 file2hash = open(each_file,'rb')
 data += file2hash.read()
 file2hash.close()
 sha256file=bitcoin.sha256(data)
 bytes+=len(data)
 data = sha256file 

 text += each_file+' '+sha256file+'\n' 
 if not quiet:
  sys.stdout.write(text)
 if stamp:
  logfile.write(text)
 data = sha256file
 text = ''

sha2564files = data

if burn:
 payto_addr = bitcoin.pubtoaddr(sha2564files)
else:
 priv = sha2564files 
 privb58 = bitcoin.encode_privkey(priv,'wif')
 pub = bitcoin.privtopub(priv)
 payto_addr = bitcoin.pubtoaddr(pub)

text += format(bytes)+' Bytes processed\n' 
text += '*sha256 refers to SHA-2/Secure Hash Algorithm 2, NIST Standard FIPS PUB 180-2\n\n'
text += 'sha256 hash value (hex)      = '+sha2564files
if burn:
 text += '\n... is used as public key ...\n'
else:
 text += '\n... is used as private key ...\n'
 text += 'Bitcoin private key (hex)    = '+priv+'\n'
 text += 'Bitcoin private key (Base58) = '+privb58
 text += '\n... deriving Bitcoin address form pivate key ...\n'

text +=  'Bitcoin Address (Base 58)    = '+payto_addr+'\n'
text +=  'Link to check address: https://blockchain.info/address/'+payto_addr+'\n'

if not quiet:
 sys.stdout.write(text)

if not stamp:
 exit(1)

logfile.write(text)
now = datetime.datetime.utcnow().strftime("%Y.%m.%d-%H:%M:%S")
text  = format(PAYTO_AMOUNT_BTC,'f')+' BTC will be transmitted to Bitcoin address ' + payto_addr+'\n'
text += 'as proof of existence of above file(s) on '+now+' UTC.\n'

if not quiet:
 sys.stdout.write(text)

logfile.write(text)

if not quiet:
 print 'Preparing transaction...'

if not yes:
 text = 'Do you really want to transmit '+format(PAYTO_AMOUNT_BTC,'f')+' BTC to '+payto_addr

 if burn:
  text += ' (WARNING - funds will be BURNED!)'
 text += ' ? y/n: '
 choice = raw_input(text).lower()
 if choice != 'y':
  sys.exit(-1)

electrum_payto = [ELECTRUM_BIN,'payto','-w',electrum_wallet_file,payto_addr,format(PAYTO_AMOUNT_BTC,'f')]

if electrum_wallet_password:
 electrum_payto += ['-W',electrum_wallet_password]

p = subprocess.Popen(electrum_payto, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
stdout_text = p.stdout.read()
stderr_text = p.stderr.read()
text = stdout_text + stderr_text

if p.wait() != 0:
 print 'Error: creating transaction failed ...'
 print ' '.join(electrum_payto)
 print text
 sys.exit(-1)

tx_json = json.loads(stdout_text)
if tx_json['complete'] != True:
 print 'Error: creating transaction failed ...'
 print ' '.join(electrum_payto)
 print text
 sys.exit(-1)
  
tx = tx_json['hex']

#broadcast tx 
electrum_broadcast = [ELECTRUM_BIN,'broadcast',tx]

p = subprocess.Popen(electrum_broadcast, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
stdout_text = p.stdout.read()
stderr_text = p.stderr.read()
text = stdout_text + stderr_text

if p.wait() != 0:
 print 'Error: broadcasting transaction failed ...'
 print ' '.join(electrum_broadcast)
 print text
 sys.exit(-1)

txid_json = json.loads(stdout_text);

if txid_json[0] != True:
 print 'Error: broadcasting transaction failed ...'
 print ' '.join(electrum_broadcast)
 print stdout_text
 sys.exit(-1)

text = 'Link to check transaction: https://blockchain.info/tx/'+txid_json[1]+'\n'
text += 'Command for reproducing:\n./'+PROG+'.py '
if burn:
 text += '--burn '
text += '-f '+' -f '.join(files_to_stamp)+'\n'

if not quiet:
 sys.stdout.write(text)
logfile.write(text)
logfile.close()

if zipfiles:
 print "Creating zip archive ...\n"
 zipfile = 'PoE-UTC='+now+'-BTC-addr='+payto_addr+'.zip'
 zipfile_cmd = 'zip -9 '+zipfile+' '+(' '.join(files_to_stamp)+' '+PROG+'.log')
 p = subprocess.Popen(zipfile_cmd,shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 stdout_text = p.stdout.read()
 stderr_text = p.stderr.read()
 text = stdout_text + stderr_text
 if p.wait() != 0:
  print 'Error: Could not create zip file'
  print zipfile_cmd
  print text
  sys.exit(-1)
 if not quiet:
  print 'Files were archived into '+zipfile

print payto_addr
sys.exit(0)




