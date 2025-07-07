# cw-soda

A CLI tool for Unix-like environments to encrypt/decrypt a CW log using NaCl. \
That's a toy I created after watching a documentary on the Enigma machine. 
I wanted to re-implement the encryption machine, update it for the 21st century, and fix all the bugs.


#### Features

- Public Key cryptography (Curve25519-XSalsa20-Poly1305)
- Key derivation (Argon2)
- Text compression (zlib, bz2, lzma)
- CRC-based error correction
- Custom Morse alphabets


#### Installation

1. Install uv: [Installation](https://docs.astral.sh/uv/getting-started/installation/)
   ```
   # Ubuntu
   % sudo snap install astral-uv --classic

   # MacOS
   % brew install uv
   ```
2. Install cw-soda:
   ```
   % uv tool install .
   ```
3. Remove cw-soda:
   ```
   % uv tool uninstall cw-soda
   ```


#### Key generation

```
% soda genkey > alice
% soda pubkey alice > alice_pub
% soda genkey | tee bob | soda pubkey - > bob_pub

% cat alice
2FDPMS0Q5SB82YN39525P2UJH1G90KB9KWR7JOYM13CEEH6W8K
```

#### Encryption

Alice sends the message to Bob:

```
% soda encrypt alice bob_pub message > encrypted
Plaintext length: 238
Ciphertext length: 320
Redundancy: 1.345

% head -c 61 encrypted
EKDBXVYICDEJVC7EM3V4VE7HCM9OD9HRDX0DAOJ8K5Y3LHV4Z0NPDBGNW6T42

% soda print encrypted 
#	A    	B    	C    	D    	E    	F    	G    	
1	EKDBX	NPDBG	FC7EX	H3URF	H3VIM	7YFLH	5NE5T	
2	VYICD	NW6T4	37KUJ	5V457	XQETZ	QU68M	21LL7	
3	EJVC7	2HUGY	JGK8T	LNDHY	WR3UI	RT382	BCOBQ	
4	EM3V4	0RGN9	6HT32	IUSN5	KH0BU	4H4HJ	90XPQ	
5	VE7HC	2BJ8F	T2SFM	ZLQL7	D1XJ7	1P683	
6	M9OD9	BQT8C	H0CNC	EMBCJ	R76OV	16VM1	
7	HRDX0	313GI	91JA6	TFO6N	4L9WG	J69CW	
8	DAOJ8	3XFZU	V2K9F	MH3G4	NGVJK	52CL2	
9	K5Y3L	EPSDT	63T5T	I1716	YZ2AQ	HY4IF	
10	HV4Z0	5OVDT	ULRZV	ZO00M	PCCEZ	7BVCR	
```

#### Decryption

Bob recieves the message from Alice:

```
% soda decrypt bob alice_pub received
A telegraph key is a specialized electrical switch used by a trained operator to transmit
text messages in Morse code in a telegraphy system.
The first telegraph key was invented by Alfred Vail, an associate of Samuel Morse.
(c) Wikipedia
Plaintext length: 238
Ciphertext length: 320
Redundancy: 1.345

% head -3 received 
EKDBX
VYICD
EJVC7

% soda print received 
#	A    	B    	C    	D    	E    	F    	G    	
1	EKDBX	NPDBG	FC7EX	H3URF	H3VIM	7YFLH	5NE5T	
2	VYICD	NW6T4	37KUJ	5V457	XQETZ	QU68M	21LL7	
3	EJVC7	2HUGY	JGK8T	LNDHY	WR3UI	RT382	BCOBQ	
4	EM3V4	0RGN9	6HT32	IUSN5	KH0BU	4H4HJ	90XPQ	
5	VE7HC	2BJ8F	T2SFM	ZLQL7	D1XJ7	1P683	
6	M9OD9	BQT8C	H0CNC	EMBCJ	R76OV	16VM1	
7	HRDX0	313GI	91JA6	TFO6N	4L9WG	J69CW	
8	DAOJ8	3XFZU	V2K9F	MH3G4	NGVJK	52CL2	
9	K5Y3L	EPSDT	63T5T	I1716	YZ2AQ	HY4IF	
10	HV4Z0	5OVDT	ULRZV	ZO00M	PCCEZ	7BVCR	
```

#### Error correction

Alice and Bob communicate the checksums to compare the files: 

<pre>
% soda find-error received
Checksum: 60
Is it correct? [y/n]: n
Checksum: 6F
Is it correct? [y/n]: y
Checksum: A3
Is it correct? [y/n]: n
Checksum: E2
Is it correct? [y/n]: y
Checksum: F
Is it correct? [y/n]: n
Checksum: 75
Is it correct? [y/n]: y
Checksum: F7
Is it correct? [y/n]: n
Checksum: 4B
Is it correct? [y/n]: y
Checksum: 40
Is it correct? [y/n]: n
Checksum: 55
Is it correct? [y/n]: y
Checksum: 57
Is it correct? [y/n]: n
The error is in: 5VV57
#	A    	B    	C    	D    	E    	F    	G    	
1	EKDBX	NPDBG	FC7EX	H3URF	H3VIM	7YFLH	5NE5T	
2	VYICD	NW6T4	37KUJ	<b><ins>5VV57</ins></b>	XQETZ	QU68M	21LL7	
3	EJVC7	2HUGY	JGK8T	LNDHY	WR3UI	RT382	BCOBQ	
4	EM3V4	0RGN9	6HT32	IUSN5	KH0BU	4H4HJ	90XPQ	
5	VE7HC	2BJ8F	T2SFM	ZLQL7	D1XJ7	1P683	
6	M9OD9	BQT8C	H0CNC	EMBCJ	R76OV	16VM1	
7	HRDX0	313GI	91JA6	TFO6N	4L9WG	J69CW	
8	DAOJ8	3XFZU	V2K9F	MH3G4	NGVJK	52CL2	
9	K5Y3L	EPSDT	63T5T	I1716	YZ2AQ	HY4IF	
10	HV4Z0	5OVDT	ULRZV	ZO00M	PCCEZ	7BVCR	
</pre>


#### Using a custom Morse alphabet

Most of the commands accept the `--baseXX` flag. The encoding must be consistent across all inputs. \
You can convert the keys with `readkey`:

```
% soda readkey --in-base36 --out-base26 alice > alice_b26
% soda readkey --in-base36 --out-base26 alice_pub > alice_pub_b26
% cat alice alice_b26 
2FDPMS0Q5SB82YN39525P2UJH1G90KB9KWR7JOYM13CEEH6W8K
BSSICITKSLKFHZXWTDFMEXAAIJNOJEZSLPGXGYJAXTBDTENSMIJIEWY

% soda genkey --base26 | tee claire | soda pubkey --base26 - > claire_pub
% soda encrypt --base26 alice_b26 claire_pub message > encrypted
Plaintext length: 238
Ciphertext length: 352
Redundancy: 1.479
```


#### Key derivation

The salt will be generated if omitted:

```
% soda kdf password > key
Salt: 81I086JO5LTH5E5EHOBHH2Z84

% soda kdf password salt
4NG87G0U9P0J4OM55Z8CPF9FIWGZRNVAIMR7YETDD8TE8O3CUZ
```


#### Compression

That works as follows:
1. The plaintext is compressed with the archiver, which adds the dictionary
2. The 16-byte MAC and 24-byte nonce are added
3. The result is encoded with Base36, which adds ~36% overhead
 
Aside from the default `--zlib`, there are more compression options. \
For a short message, the `--uncompressed` option provides smaller output. 
For a long text, the `--bz2` showed the best results. \
Overall, encrypting a letter into 1.345 letters is a working solution.

```
% soda encrypt alice bob_pub message --zlib > encrypted
Plaintext length: 238
Ciphertext length: 320
Redundancy: 1.345
% soda encrypt alice bob_pub message --bz2 > encrypted
Plaintext length: 238
Ciphertext length: 381
Redundancy: 1.601
% soda encrypt alice bob_pub message --lzma > encrypted
Plaintext length: 238
Ciphertext length: 372
Redundancy: 1.563
% soda encrypt alice bob_pub message --uncompressed > encrypted
Plaintext length: 238
Ciphertext length: 431
Redundancy: 1.811
```


#### Applications

The project can come in handy beyond the telegraphy system. \
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


#### Getting help

All commands have `[-h | --help]` option:

```
% soda --help
Usage: soda [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  decrypt     Decrypt message
  encrypt     Encrypt message
  find-error  Find error
  genkey      Generate Private Key
  kdf         Derive key
  print       Print CW table
  pubkey      Get Public Key
  readkey     Read key
```