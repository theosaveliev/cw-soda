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

All commands have `[-h | --help]` option:

```
% soda --help
Usage: soda [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  decrypt     Decrypt the message
  encrypt     Encrypt the message
  find-error  Find the error
  genkey      Generate a Private or a Secret Key
  kdf         Derive a Private or a Secret Key
  print       Print as table
  pubkey      Get the Public Key
  readkey     Read a Private or a Secret Key
```


## Public Key encryption
#### Key generation

```
% soda genkey > alice
% soda pubkey alice > alice_pub
% soda genkey | tee bob | soda pubkey - > bob_pub

% cat alice
1RNSV1XN7EY6LIMRGQLM04ZSAV2I4QZITJTPJ8KEUSTZLL6XPV
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
53D9P20CSQMJ1S5VA1HRUYHRRTUF3D15810MVA8M8GSTP19FFF1XGK7VH5N8R

% soda print encrypted 
#	A    	B    	C    	D    	E    	F    	G    	
1	53D9P	1XGK7	FWYUF	7UWY2	EC7V3	30K04	5C59X	
2	20CSQ	VH5N8	VLO2Z	JA2VG	NL3MR	X52QD	9M0U5	
3	MJ1S5	RF292	HN80W	TPWM8	M5C61	USEBK	F1BM4	
4	VA1HR	YQFGM	09PVJ	Q8R2U	4WYK0	860YH	035UD	
5	UYHRR	MWTBZ	RYV57	JJTQF	NDB1J	Q7DHY	
6	TUF3D	NZU58	20ERX	71TGC	1ST62	C8D0E	
7	15810	Y4EIM	ZD01N	1PF7W	RIQFR	AC4UG	
8	MVA8M	6I5EN	KTU89	NQB63	5YHSM	55A51	
9	8GSTP	NU71Q	6NNUP	R8A4G	AH1UC	ORVCB	
10	19FFF	GG8WT	UE28K	DY151	DFJPR	O7C6Q	
```

#### Decryption

Bob recieves the message from Alice:

```
% head -3 received 
53D9P
20CSQ
MJ1S5

% soda print received
#	A    	B    	C    	D    	E    	F    	G    	
1	53D9P	1XGK7	FWYUF	7UWY2	EC7V3	30K04	5C59X	
2	20CSQ	VH5N8	VLO2Z	JA2VG	NL3MR	X52QD	9M0U5	
3	MJ1S5	RF292	HN80W	TPWM8	M5C61	USEBK	F1BM4	
4	VA1HR	YQFGM	09PVJ	Q8R2U	4WYK0	860YH	035UD	
5	UYHRR	MWTBZ	RYV57	JJTQF	NDB1J	Q7DHY	
6	TUF3D	NZU58	20ERX	71TGC	1ST62	C8D0E	
7	15810	Y4EIM	ZD01N	1PF7W	RIQFR	AC4UG	
8	MVA8M	6I5EN	KTU89	NQB63	5YHSM	55A51	
9	8GSTP	NU71Q	6NNUP	R8A4G	AH1UC	ORVCB	
10	19FFF	GG8WT	UE28K	DY151	DFJPR	O7C6Q	

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

The encryption commands accept the `--symmetric` flag:

```
% soda genkey --symmetric | tee secret
4B6OC480WUKTVUK0RW7M4MKI7AH1BBJGPAIBLVO4XH9ZWLHJSC

% soda encrypt message secret --symmetric > encrypted
Plaintext length: 238
Ciphertext length: 320
Overhead: 1.345

% head -c 61 encrypted
2CEPJZL66UWKLLWHYB90PKMUAD80KOZ2JCZZ5P61AXSXUZXU67S1M4VG8DP7W

% soda decrypt encrypted secret --symmetric
A telegraph key is a specialized electrical switch used by a trained operator to transmit
text messages in Morse code in a telegraphy system.
The first telegraph key was invented by Alfred Vail, an associate of Samuel Morse.
(c) Wikipedia
Plaintext length: 238
Ciphertext length: 320
Overhead: 1.345
```


## Key derivation

The KDF function derives a Private or a Secret Key from the password and salt. \
The salt will be generated if omitted.
It can be provided as an arbitrary string, 
in which case you might want to add the `--hash` flag to hash the input.

```
% echo qwerty > password
% soda kdf password | tee private
Salt: 4IO9S8KNP0HEA3XF7DWULSPVO
5XWXPUA8GDRH0088FUP1OYOIKNIBJBWCXXRRLC7Q89NJOM34KJ

% echo 12345 > salt
% soda kdf password salt --hash | tee private
Salt: 3AIK26Z5MZ294C6SN7WV21X
8C7DHO6XG2YYAC8YLLI7YBTKEWZE7IJJ0ZIM70MJ8F1SF0BTP

% echo 3AIK26Z5MZ294C6SN7WV21X | soda kdf password - | tee private
Salt: 3AIK26Z5MZ294C6SN7WV21X
8C7DHO6XG2YYAC8YLLI7YBTKEWZE7IJJ0ZIM70MJ8F1SF0BTP

% soda kdf password --symmetric | tee secret
Salt: F4VJY0A6DYVF4TBR0ZM44BCWA
2BLRBM6BND8B5M3QJSMVMB4WMJGQJ8181FQL2B1J8MXANKGQZM
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
% soda find-error received 
Checksum: 80
Is it correct? [y/n]: n
Checksum: A0
Is it correct? [y/n]: y
Checksum: EC
Is it correct? [y/n]: n
Checksum: 93
Is it correct? [y/n]: y
Checksum: 16
Is it correct? [y/n]: n
Checksum: B9
Is it correct? [y/n]: y
Checksum: 6A
Is it correct? [y/n]: n
Checksum: A4
Is it correct? [y/n]: y
Checksum: 62
Is it correct? [y/n]: n
Checksum: D0
Is it correct? [y/n]: y
Checksum: F
Is it correct? [y/n]: n
The error is in: JA2VG
#	A    	B    	C    	D    	E    	F    	G    	
1	53D9P	1XGK7	FWYUF	7UWY2	EC7V3	30K04	5C59X	
2	20CSQ	VH5N8	VLO2Z	<b><ins>JA2VG</ins></b>	NL3MR	X52QD	9M0U5	
3	MJ1S5	RF292	HN80W	TPWM8	M5C61	USEBK	F1BM4	
4	VA1HR	YQFGM	09PVJ	Q8R2U	4WYK0	860YH	035UD	
5	UYHRR	MWTBZ	RYV57	JJTQF	NDB1J	Q7DHY	
6	TUF3D	NZU58	20ERX	71TGC	1ST62	C8D0E	
7	15810	Y4EIM	ZD01N	1PF7W	RIQFR	AC4UG	
8	MVA8M	6I5EN	KTU89	NQB63	5YHSM	55A51	
9	8GSTP	NU71Q	6NNUP	R8A4G	AH1UC	ORVCB	
10	19FFF	GG8WT	UE28K	DY151	DFJPR	O7C6Q	
</pre>


## Using a custom Morse alphabet

Most of the commands accept the `--baseXX` flag. The encoding must be consistent across all inputs. \
You can convert the keys with `readkey`:

```
% soda readkey --in-base36 --out-base26 alice > alice_b26
% soda readkey --in-base36 --out-base26 alice_pub > alice_pub_b26
% cat alice alice_b26 
1RNSV1XN7EY6LIMRGQLM04ZSAV2I4QZITJTPJ8KEUSTZLL6XPV
BGOUUIJGCIWGEQKBRVRAFRKAQSLJVPFUTNLOYCPNXXJQAKGKDHNIRUX

% soda genkey --base26 | tee claire | soda pubkey --base26 - > claire_pub
% soda encrypt message alice_b26 claire_pub --base26 > encrypted 
Plaintext length: 238
Ciphertext length: 352
Overhead: 1.479

% soda genkey -h
Usage: soda genkey [OPTIONS]

  Generate a Private or a Secret Key

Options:
  Encoding: [mutually_exclusive]
    --base10
    --base16
    --base26
    --base31
    --base36                      (default)
    --base41
    --base64
  --symmetric
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