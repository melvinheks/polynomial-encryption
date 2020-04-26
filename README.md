# polynomial-encryption
Encryption scheme poc based on Newton's method to solve for root of a secret polynomial acting as a key

For numerical issues in scientific programming project idea based on https://airccj.org/CSCP/vol3/csit3214.pdf

```
usage: PolynomialEncryption.py [-h] [--genkey GENKEY] [--keyfile KEYFILE]
                               [--encrypt ENCRYPT] [--decrypt DECRYPT]

Newton's method based encryption

optional arguments:
  -h, --help         show this help message and exit
  --genkey GENKEY    Generate a new key
  --keyfile KEYFILE  The keyfile to encrypt decrypt with
  --encrypt ENCRYPT  The file to encrypt
  --decrypt DECRYPT  The file to decrypt
```
