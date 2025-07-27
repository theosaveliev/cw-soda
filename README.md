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
#### Package manager

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Install cw-soda:
   ```
   % uv tool install .
   ```
3. Remove cw-soda:
   ```
   % uv tool uninstall cw-soda
   ```

#### Docker

```
% docker run -it --rm -h cw-soda -v .:/home/ubuntu/host nett/cw-soda:v0.4.3
```


## Getting help

All commands have `[-h | --help]` option.


## Public Key encryption
#### Key generation

```
% soda genkey > alice
% soda pubkey alice > alice_pub
% soda genkey | tee bob | soda pubkey - > bob_pub

% cat alice
41YZNX5BF43P1AHY4E6NTMZYD535UWQ7ND16L0H4WQN2V9XK6E
```

#### Encryption

Alice sends the message to Bob:

```
% cat message 
A telegraph key is a specialized electrical switch used by a trained operator to transmit
text messages in Morse code in a telegraphy system.
The first telegraph key was invented by Alfred Vail, an associate of Samuel Morse.
(c) Wikipedia

% soda encrypt alice bob_pub message > encrypted
Plaintext length: 238
Ciphertext length: 320
Overhead: 1.345

% head -c 61 encrypted
LL0463X97K62C3RNPC6S0JKL4HNLCURI4TMGU7D19LUDPN0PFATCW2WSRGQ7J

% soda print encrypted
#	A    	B    	C    	D    	E    	F    	G    	
1	LL046	TCW2W	GAQ8H	VQKE7	GCE7T	RH9XF	I1LVG	
2	3X97K	SRGQ7	HK31V	1E2O3	4W1DC	6BTW8	DUW9L	
3	62C3R	JLAK3	5AWIR	BH03B	6UOIT	P6RK8	1UZHQ	
4	NPC6S	YI3AE	59AAV	OW5E9	OFNCP	7ZF6U	A9OP2	
5	0JKL4	JRCB5	I19SX	ZMDD9	2LKEF	XUSBJ	
6	HNLCU	JGR0T	V1ZZX	MPR9N	2RORT	RW9KC	
7	RI4TM	8BDAK	HJZEI	S04T1	7LXTN	STYJL	
8	GU7D1	DY1J7	8VRJ5	JJP40	48F8O	39FZK	
9	9LUDP	IJ8ZL	LG5UH	VB32L	6BTNG	NDVF9	
10	N0PFA	5QZ30	9PPH6	AL67U	9VV3O	MPMNM	
```

#### Decryption

Bob writes down the CW groups as he receives the message from Alice:

```
% head -3 received 
ll046
3x97k
62c3r

% soda print received
#	A    	B    	C    	D    	E    	F    	G    	
1	LL046	TCW2W	GAQ8H	VQKE7	GCE7T	RH9XF	I1LVG	
2	3X97K	SRGQ7	HK31V	1E2O3	4W1DC	6BTW8	DUW9L	
3	62C3R	JLAK3	5AWIR	BH03B	6UOIT	P6RK8	1UZHQ	
4	NPC6S	YI3AE	59AAV	OW5E9	OFNCP	7ZF6U	A9OP2	
5	0JKL4	JRCB5	I19SX	ZMDD9	2LKEF	XUSBJ	
6	HNLCU	JGR0T	V1ZZX	MPR9N	2RORT	RW9KC	
7	RI4TM	8BDAK	HJZEI	S04T1	7LXTN	STYJL	
8	GU7D1	DY1J7	8VRJ5	JJP40	48F8O	39FZK	
9	9LUDP	IJ8ZL	LG5UH	VB32L	6BTNG	NDVF9	
10	N0PFA	5QZ30	9PPH6	AL67U	9VV3O	MPMNM	

% soda decrypt bob alice_pub received 
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
% soda encrypt-secret shared message > encrypted
Plaintext length: 238
Ciphertext length: 320
Overhead: 1.345

% soda decrypt-secret shared encrypted
A telegraph key is a specialized electrical switch used by a trained operator to transmit
text messages in Morse code in a telegraphy system.
The first telegraph key was invented by Alfred Vail, an associate of Samuel Morse.
(c) Wikipedia
Plaintext length: 238
Ciphertext length: 320
Overhead: 1.345
```


## Key derivation

The KDF function derives the key from the password and salt. 
It accepts different profiles: interactive, moderate, and sensitive. \
The salt is hashed (Blake2) by default, which can be disabled by passing `--raw-salt` 

```
% echo qwerty > password
% echo 12345 > salt
% soda kdf password salt
8C7DHO6XG2YYAC8YLLI7YBTKEWZE7IJJ0ZIM70MJ8F1SF0BTP

% soda kdf password salt --profile sensitive
3SMHEPX5RPTW7JWFJVF783EEC1FH9RXYBZN16W49UBN1WJNTHH

% soda genkey > salt
% soda kdf password salt --raw-salt
5NQ87O2FLSHR6YS6EMJHI1X9RH5CTV4GKEN4K4QNAX0MTDHV20
```


## Text compression

That works as follows:
1. The plaintext is compressed with the compression lib
2. The 16-byte MAC and 24-byte nonce are added
3. The result is encoded with Base36, which adds ~36% overhead

Aside from the default zlib, there are more compression options. \
For a short message, the raw option provides smaller output.
For a long text, the bz2 showed the best results. \
Overall, encrypting a letter into 1.345 letters is a working solution.

```
% soda encrypt alice bob_pub message --compression zlib > /dev/null
Plaintext length: 238
Ciphertext length: 320
Overhead: 1.345
% soda encrypt alice bob_pub message --compression bz2 > /dev/null 
Plaintext length: 238
Ciphertext length: 381
Overhead: 1.601
% soda encrypt alice bob_pub message --compression lzma > /dev/null
Plaintext length: 238
Ciphertext length: 371
Overhead: 1.559
% soda encrypt alice bob_pub message --compression raw > /dev/null 
Plaintext length: 238
Ciphertext length: 430
Overhead: 1.807
```


## Error correction

Alice and Bob communicate the checksums to compare the files: 

<pre>
% soda find-error received 
Checksum: 1B
Is it correct? [y/n]: n
Checksum: 14
Is it correct? [y/n]: y
Checksum: 95
Is it correct? [y/n]: n
Checksum: 6D
Is it correct? [y/n]: n
Checksum: 29
Is it correct? [y/n]: n
Checksum: F9
Is it correct? [y/n]: n
Checksum: 10
Is it correct? [y/n]: n
The error is in: 8BBAK
#	A    	B    	C    	D    	E    	F    	G    	
1	LL046	TCW2W	GAQ8H	VQKE7	GCE7T	RH9XF	I1LVG	
2	3X97K	SRGQ7	HK31V	1E2O3	4W1DC	6BTW8	DUW9L	
3	62C3R	JLAK3	5AWIR	BH03B	6UOIT	P6RK8	1UZHQ	
4	NPC6S	YI3AE	59AAV	OW5E9	OFNCP	7ZF6U	A9OP2	
5	0JKL4	JRCB5	I19SX	ZMDD9	2LKEF	XUSBJ	
6	HNLCU	JGR0T	V1ZZX	MPR9N	2RORT	RW9KC	
7	RI4TM	<b><ins>8BBAK</ins></b>	HJZEI	S04T1	7LXTN	STYJL	
8	GU7D1	DY1J7	8VRJ5	JJP40	48F8O	39FZK	
9	9LUDP	IJ8ZL	LG5UH	VB32L	6BTNG	NDVF9	
10	N0PFA	5QZ30	9PPH6	AL67U	9VV3O	MPMNM	
</pre>


## Encoding

The cw-soda supports various encodings:

- Base26 (Latin)
- Base31 (Cyrillic)
- Base36 (Latin with numbers)
- Base64 (RFC 3548)
- Base94 (ASCII printable)
- Binary

```
% soda genkey --encoding base26 | tee key26  
DROFNIXGVGDTLEAVZDNGXVYRLYOAOSDFGXZMRVUJRCCLKOVYPVCNITT

% soda encrypt-secret key26 message --key-encoding base26 --data-encoding base26 > encrypted
Plaintext length: 238
Ciphertext length: 353
Overhead: 1.483

% head -c 55 encrypted
BWOUCHPOOHJCTUEXGVEGDSVKXOPOBUXOAECZUHHYUZGBALFKMRHZDJE
```


## Applications

The project may come in handy beyond the telegraphy system. 


#### Printed backup

I printed a backup of my Google credentials. Here comes a fake version of the backup:

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


#### Password source

```
% echo 'A quote from a book or a poem.' > quote
% echo google.com | soda kdf quote - --encoding base94
"!p$u{e%_8Fe;)a\sg-!O1KD<ptKV@booBHuwKXs
```


#### Getting WireGuard key from password

The keys are compatible with WireGuard, so you can use the KDF function for keying.

```
% wg genkey | tee wg_key | wg pubkey
kszDHQ9ZZJuwSZ8OSz99Hx7WNIFaTvmnvUlE+OALmDo=
% soda pubkey wg_key --encoding base64
kszDHQ9ZZJuwSZ8OSz99Hx7WNIFaTvmnvUlE+OALmDo=
```


## Compatibility

During the initial development (versions prior to 1.0.0), 
I reserve the right to break backwards compatibility. 
