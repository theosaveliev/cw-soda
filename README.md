# cw-soda

A CLI tool for Unix-like environments to encrypt/decrypt a CW log using NaCl. \
That's a toy I created after watching a documentary on the Enigma machine. 
I wanted to re-implement the encryption machine, update it for the 21st century, and fix all the bugs.


#### Features

- Public Key encryption (Curve25519-XSalsa20-Poly1305)
- Secret Key encryption (XSalsa20-Poly1305)
- Key derivation (Argon2)
- Text compression (zlib, bz2, lzma)
- CRC-based error correction
- Custom Morse alphabets


## Installation

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Install cw-soda:
   ```
   % uv tool install .
   ```
3. Remove cw-soda:
   ```
   % uv tool uninstall cw-soda
   ```


## Getting help

All commands have `--help` option:

```
% soda --help
Usage: soda [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  decrypt     Decrypt message
  encode      Encode file
  encrypt     Encrypt message
  find-error  Find error
  genkey      Generate Private Key
  kdf         Derive Private Key
  print       Print table
  pubkey      Get Public Key
```


## Public Key encryption
#### Key generation

```
% soda genkey > alice
% soda pubkey alice > alice_pub
% soda genkey | tee bob | soda pubkey - > bob_pub

% cat alice
65AV4JO2P750P52WHSMZIQEM09483SZCACZIO9V2ALBBNI2GFQ
```

#### Encryption

Alice sends the message to Bob:

```
% cat message 
A telegraph key is a specialized electrical switch used by a trained operator to transmit
text messages in Morse code in a telegraphy system.
The first telegraph key was invented by Alfred Vail, an associate of Samuel Morse.
(c) Wikipedia

% soda encrypt message alice bob_pub > encrypted
Plaintext length: 238
Ciphertext length: 320
Overhead: 1.345

% head -c 61 encrypted
E83LSBHQIL8EDX1JZP07GYH4UQMRCP03QKPN2ASH59SO7HHNDSK51ZK4FDKPK

% soda print encrypted 
#	A    	B    	C    	D    	E    	F    	G    	
1	E83LS	K51ZK	YI92O	RBBVR	SJLLJ	NQD7Q	0K5QP	
2	BHQIL	4FDKP	AF8LP	YCH3L	94AWX	DBVMU	8G28D	
3	8EDX1	KQAEW	TSQ8C	22VL1	R4G4Y	MNTVD	40GNZ	
4	JZP07	AFO1Q	WXBE3	51SUU	FFREO	R1A4P	CWU55	
5	GYH4U	JXXBN	SWE75	LKGTT	8M64Z	U7FPQ	
6	QMRCP	SVXW9	7U0JI	G4MCB	8AQ5F	7XUCQ	
7	03QKP	I4W9R	Y3D5N	1FNA7	O6PIB	WJ3JL	
8	N2ASH	65256	NWXKW	3A47D	579CT	RICC7	
9	59SO7	XN0FU	KAF6L	9DZEM	TY7CL	LJ0RP	
10	HHNDS	P854Y	A9Z58	BRNV7	HY8H7	TR268	
```

#### Decryption

Bob recieves the message from Alice:

```
% head -3 received 
E83LS
BHQIL
8EDX1

% soda print received
#	A    	B    	C    	D    	E    	F    	G    	
1	E83LS	K51ZK	YI92O	RBBVR	SJLLJ	NQD7Q	0K5QP	
2	BHQIL	4FDKP	AF8LP	YCH3L	94AWX	DBVMU	8G28D	
3	8EDX1	KQAEW	TSQ8C	22VL1	R4G4Y	MNTVD	40GNZ	
4	JZP07	AFO1Q	WXBE3	51SUU	FFREO	R1A4P	CWU55	
5	GYH4U	JXXBN	SWE75	LKGTT	8M64Z	U7FPQ	
6	QMRCP	SVXW9	7U0JI	G4MCB	8AQ5F	7XUCQ	
7	03QKP	I4W9R	Y3D5N	1FNA7	O6PIB	WJ3JL	
8	N2ASH	65256	NWXKW	3A47D	579CT	RICC7	
9	59SO7	XN0FU	KAF6L	9DZEM	TY7CL	LJ0RP	
10	HHNDS	P854Y	A9Z58	BRNV7	HY8H7	TR268

% soda decrypt received bob alice_pub  
A telegraph key is a specialized electrical switch used by a trained operator to transmit
text messages in Morse code in a telegraphy system.
The first telegraph key was invented by Alfred Vail, an associate of Samuel Morse.
(c) Wikipedia
Plaintext length: 238
Ciphertext length: 320
Overhead: 1.345
```


## Secret Key encryption

Alice and Bob share a key for symmetric encryption:

```
% soda genkey > shared

% soda encrypt message shared > encrypted
Plaintext length: 238
Ciphertext length: 321
Overhead: 1.349

% soda decrypt encrypted shared
A telegraph key is a specialized electrical switch used by a trained operator to transmit
text messages in Morse code in a telegraphy system.
The first telegraph key was invented by Alfred Vail, an associate of Samuel Morse.
(c) Wikipedia
Plaintext length: 238
Ciphertext length: 321
Overhead: 1.349
```


## Key derivation

The KDF function derives the key from the password and salt. \
The salt will be generated if omitted. \
The salt is hashed by default, which can be disabled by passing `--raw-salt`

```
% echo qwerty > password
% soda kdf password
Salt: 9RTY9ESH7RK4GUMX6DINC43O1
3SY5V8E1M4ZX2A5YIYH3R6Q0DQ8QPT6WIADAGO36UFTBFZYWDZ

% echo 12345 > salt
% soda kdf password salt
Salt: 3AIK26Z5MZ294C6SN7WV21X
8C7DHO6XG2YYAC8YLLI7YBTKEWZE7IJJ0ZIM70MJ8F1SF0BTP

% echo 3AIK26Z5MZ294C6SN7WV21X > salt
% soda kdf password salt --raw-salt
Salt: 3AIK26Z5MZ294C6SN7WV21X
8C7DHO6XG2YYAC8YLLI7YBTKEWZE7IJJ0ZIM70MJ8F1SF0BTP
```


## Text compression

That works as follows:
1. The plaintext is compressed with the compression lib
2. The 16-byte MAC and 24-byte nonce are added
3. The result is encoded with Base36, which adds ~36% overhead

Aside from the default `--zlib`, there are more compression options. \
For a short message, the `--uncompressed` option provides smaller output.
For a long text, the `--bz2` showed the best results. \
Overall, encrypting a letter into 1.345 letters is a working solution.

```
% soda encrypt message alice bob_pub --zlib > encrypted
Plaintext length: 238
Ciphertext length: 320
Overhead: 1.345

% soda encrypt message alice bob_pub --bz2 > encrypted
Plaintext length: 238
Ciphertext length: 381
Overhead: 1.601

% soda encrypt message alice bob_pub --lzma > encrypted
Plaintext length: 238
Ciphertext length: 372
Overhead: 1.563

% soda encrypt message alice bob_pub --uncompressed > encrypted
Plaintext length: 238
Ciphertext length: 431
Overhead: 1.811
```


## Error correction

Alice and Bob communicate the checksums to compare the files: 

<pre>
% soda find-error encrypted 
Checksum: F8
Is it correct? [y/n]: n
Checksum: 58
Is it correct? [y/n]: y
Checksum: C9
Is it correct? [y/n]: n
Checksum: 66
Is it correct? [y/n]: n
Checksum: BC
Is it correct? [y/n]: n
Checksum: 94
Is it correct? [y/n]: n
Checksum: 8D
Is it correct? [y/n]: n
The error is in: I4W9R
#	A    	B    	C    	D    	E    	F    	G    	
1	E83LS	K51ZK	YI92O	RBBVR	SJLLJ	NQD7Q	0K5QP	
2	BHQIL	4FDKP	AF8LP	YCH3L	94AWX	DBVMU	8G28D	
3	8EDX1	KQAEW	TSQ8C	22VL1	R4G4Y	MNTVD	40GNZ	
4	JZP07	AFO1Q	WXBE3	51SUU	FFREO	R1A4P	CWU55	
5	GYH4U	JXXBN	SWE75	LKGTT	8M64Z	U7FPQ	
6	QMRCP	SVXW9	7U0JI	G4MCB	8AQ5F	7XUCQ	
7	03QKP	<b><ins>I4W9R</ins></b>	Y3D5N	1FNA7	O6PIB	WJ3JL	
8	N2ASH	65256	NWXKW	3A47D	579CT	RICC7	
9	59SO7	XN0FU	KAF6L	9DZEM	TY7CL	LJ0RP	
10	HHNDS	P854Y	A9Z58	BRNV7	HY8H7	TR268	

% soda find-error received
Checksum: 36
Is it correct? [y/n]: n
Checksum: 58
Is it correct? [y/n]: y
Checksum: 7
Is it correct? [y/n]: n
Checksum: 15
Is it correct? [y/n]: n
Checksum: 9A
Is it correct? [y/n]: n
Checksum: 71
Is it correct? [y/n]: n
Checksum: F4
Is it correct? [y/n]: n
The error is in: IVW9R
#	A    	B    	C    	D    	E    	F    	G    	
1	E83LS	K51ZK	YI92O	RBBVR	SJLLJ	NQD7Q	0K5QP	
2	BHQIL	4FDKP	AF8LP	YCH3L	94AWX	DBVMU	8G28D	
3	8EDX1	KQAEW	TSQ8C	22VL1	R4G4Y	MNTVD	40GNZ	
4	JZP07	AFO1Q	WXBE3	51SUU	FFREO	R1A4P	CWU55	
5	GYH4U	JXXBN	SWE75	LKGTT	8M64Z	U7FPQ	
6	QMRCP	SVXW9	7U0JI	G4MCB	8AQ5F	7XUCQ	
7	03QKP	<b><ins>IVW9R</ins></b>	Y3D5N	1FNA7	O6PIB	WJ3JL	
8	N2ASH	65256	NWXKW	3A47D	579CT	RICC7	
9	59SO7	XN0FU	KAF6L	9DZEM	TY7CL	LJ0RP	
10	HHNDS	P854Y	A9Z58	BRNV7	HY8H7	TR268	
</pre>


## Using a custom Morse alphabet

The cw-soda supports various encodings (alphabets), which can be set with the `--baseXX` flag. \
The encoding must be consistent across all inputs. \
You can convert the keys with `encode`:

```
% soda encode alice --out-base26 > alice26
% soda encode alice_pub --out-base26 > alice_pub26
% cat alice alice26 
65AV4JO2P750P52WHSMZIQEM09483SZCACZIO9V2ALBBNI2GFQ
EJFRSZGDBILRUARMXRIVBXLQODRFKEOFFGDVJVZIFECDGHSMIVDSAZM

% soda genkey --base26 | tee claire | soda pubkey --base26 - > claire_pub
% soda encrypt message alice26 claire_pub --base26 > encrypted 
Plaintext length: 238
Ciphertext length: 353
Overhead: 1.483

% soda genkey -h
Usage: soda genkey [OPTIONS]

  Generate Private Key

Options:
  Encoding: [mutually_exclusive]
    --base10
    --base16
    --base26
    --base31
    --base36                      (default)
    --base41
    --base64
    --base94
  -h, --help                      Show this message and exit.
```


## Applications

The project may come in handy beyond the telegraphy system. \
For example, I printed a backup of my Google credentials. 
Here comes a fake version of the backup:

```
Password: +uMdh%~Sfmo[#CmFwJ4F

2fa recovery codes
1. 2772 3133	6. 5213 7230
2. 2826 1006	7. 8700 2651
3. 8721 2775	8. 3677 3062
4. 0384 0581	9. 0158 6842
5. 1650 3372	10. 3501 5000
```

That was printed as follows:

```
#	A    	B    	C    	D    	E    	F    	
1	8RNON	BYB65	CJIG9	138KD	MI7RT	6ED1U	
2	MA2A4	KBIHN	BTRXC	QALK8	F9QUT	TKW39	
3	07TD5	VH6RJ	2C8W0	TYHK2	K6QAL	X7GW3	
4	6MAD6	VE2XJ	LDKJU	O73TE	Z55YP	XXVSJ	
5	9ZSCM	MP901	XVYIZ	D13E2	FPJH5	HA06Y	
6	H3P14	HKAWA	3ALLI	8UUMZ	ZVX3Q	BYTST	
7	D6Z0S	V02OO	LCY38	0WEA1	STD28	YW3T9	
8	R6Q7D	PFR28	XYCWR	YG8U2	6YMHH	KVWUN	
9	YPZ2S	LG77O	G747X	FVZIT	M1TZP	JT5A8	
10	H7BLJ	XMVS8	8ZHOB	ACLHX	P8T4T	NYYE	
```

In this scenario, I lose all of my electronic devices simultaneously. \
That is plausible because I was robbed in Georgia, so the risk exists. 


Another usage is a password source:

```
% echo 'A quote from a book or a poem.' > quote
% echo 'google.com' > website
% soda kdf quote website --base94
Salt: "SNx=<L1;<.B#]QWEx3u
"!p$u{e%_8Fe;)a\sg-!O1KD<ptKV@booBHuwKXs
```