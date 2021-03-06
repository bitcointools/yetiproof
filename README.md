


# **yetiproof**

Command line time stamping on the Bitcoin blockchain.

## Requirements

- Linux (tested on Ubuntu 14.04 LTS)
- python 2
- python module 'bitcoin' 
- Electrum wallet (2.6.3 or higher) with a some very small BTC funds in your electrum wallet 


## Description

yetiproof.py generates a sha256 hash on a list of files, a Bitcoin address is generated from the hash and a small amount of BTC is transmitted to that address as proof of existence (PoE) on the information in the given files. It is a command line tool written for easy integration into environments like 'make'. 

There are two payment modes selectable: 'burn' and 'non-burn'. In 'burn' mode the hash is used as public key. The transmitted funds are lost, because the private key is unknown. In 'non-burn' mode the hash is used as private key and the transmitted funds can be later retrieved back or spent otherwise. In both cases the transactions are recorded on the Bitcoin blockchain forever, but certain nodes (pruning) might keep only transactions with currently existing amounts. 

yetiproof.py documents the time stamping procedure with file names, keys, addresses, transactions IDs and an instruction how to reproduce the key generation into a file. This log file is then archived into a zip file along with the list of files which were hashed. The zip file must be saved for a potential proof of existence challenge in future. The purpose of the zip archive is to prevent accidental alteration of the hashed files and keep all required data in a single place. The zip file creation can be disabled per command line option if the user wants to apply a different archiving method.

## Installation


Install Electrum wallet, if you don't already have it:

`sudo pip install https://download.electrum.org/2.6.4/Electrum-2.6.4.tar.gz`

Install python bitcoin module:

`sudo pip install bitcoin`

Install yetiproof:

`git clone https://github.com/eharvest/yetiproof.git` 


## Usage 

Example output (we are time stamping the python script itself):

```
$ ./yetiproof.py -f yetiproof.py --stamp --burn --wallet /home/yetiproof/.electrum/wallets/timestampingfunds
yetiproof 0.02
Starting electrum ...
starting daemon (PID 12414)
File(s) to be hashed by sha256*:
yetiproof.py b8a858ade9328c224a12c484a8ff7fa3d85bebde6d83ae9e8b0aa15df5391a62
8248 Bytes processed
*sha256 refers to SHA-2/Secure Hash Algorithm 2, NIST Standard FIPS PUB 180-2

sha256 hash value (hex)      = b8a858ade9328c224a12c484a8ff7fa3d85bebde6d83ae9e8b0aa15df5391a62
... is used as public key ...
Bitcoin Address (Base 58)    = 16LP3pk1GnYXxyjBmWPK26QPifYcF4E4xa
Link to check address: https://blockchain.info/address/16LP3pk1GnYXxyjBmWPK26QPifYcF4E4xa
0.000100 BTC will be transmitted to Bitcoin address 16LP3pk1GnYXxyjBmWPK26QPifYcF4E4xa
as proof of existence of above file(s) on 2016.04.26-02:39:24 UTC.
Preparing transaction...
Do you really want to transmit 0.000100 BTC to 16LP3pk1GnYXxyjBmWPK26QPifYcF4E4xa (WARNING - funds will be BURNED!) ? y/n: y
Password:
Link to check transaction: https://blockchain.info/tx/91d2970e44142d9ab6e248c02c70838378296a372d3d8f2d9a09de00e88b26a9
Command for reproducing:
./yetiproof.py --burn -f yetiproof.py
Creating zip archive ...

Files were archived into PoE-UTC=2016.04.26-02:39:24-BTC-addr=16LP3pk1GnYXxyjBmWPK26QPifYcF4E4xa.zip
16LP3pk1GnYXxyjBmWPK26QPifYcF4E4xa
$
```

Follow the links in order to verify the time stamp transaction. 

The payment amount is hard coded into the python script, but it can be changed easily:

`PAYTO_AMOUNT_BTC = 0.0001 # payment amount`

To enable dynamic fees, start Electrum, go to "Tools"->"Preferences"->"Transactions" and enable "Dynamic Fees", quit Electrum.

![](/pics/electrumfees.png)


Usage examples:

1) Time stamping, wallet password on the command line: 

```
$./yetiproof.py -f yetiproof.py --stamp --wallet </path/to/electrum-wallet/walletfile> --passwd <wallet-password>
```

2) Time stamping, wallet password on the command line, burn mode: 

```
$./yetiproof.py -f yetiproof.py --stamp --burn --wallet </path/to/electrum-wallet/walletfile> --passwd <wallet-password>
```

3) Reproducing:

```
$./yetiproof.py -f yetiproof.py 
```

4) Reproducing, burn mode:

```
$./yetiproof.py -f yetiproof.py --burn
```
A Bitcoin wallet is not required when reproducing. Follow the link to verify the time stamp transaction.

5) Help:

```
$./yetiproof.py -h|--help
 usage: yetiproof.py [-h] [--version] [-q] -f FILES_TO_STAMP [--burn] [--stamp]
                    [--yes] [--wallet WALLET_FILE] [--passwd WALLET_PASSWORD]
                    [--nozip]

Command line time stamping on the bitcoin blockchain. A hash is generated for
given files, a bitcoin address is generated from the hash and a small amount
of BTC is transmitted to that address as proof of existence.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -q, --quiet           Quiet mode
  -f FILES_TO_STAMP, --file FILES_TO_STAMP
                        File(s) to be stamped on the bitcoin blockchain,
                        allows multiple files, each file must be preceded with
                        -f
  --burn                burn mode, funds are lost forever!, default: non-burn
  --stamp               Stamp file(s) on the blockchain, default: regenerate
                        hash and bitcoin (private key and) address (proof)
  --yes                 Do not ask before sending funds, default: do ask
  --wallet WALLET_FILE  /path/to/wallet/file (required with -s|--stamp)
  --passwd WALLET_PASSWORD
                        Wallet password (optional, will be prompted, if not
                        given)
  --nozip               Do not archive file(s) into zip file, default: create
                        zip archive

```


Note:
_It is important that name(s), street address(es), phone number(s) and other information in at least in one of the files to be time stamped are included. Then the proof of existence  is clearly linked to a certain person and cannot be claimed by a different person, since this information cannot be altered without altering the hash. For convinience it is recommended that yetiproof.py is included on the list of files to be hashed (then it will be automatically included into the zip archive)._
