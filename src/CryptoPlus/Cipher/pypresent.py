# fully based on standard specifications: http://www.crypto.ruhr-uni-bochum.de/imperia/md/content/texte/publications/conferences/present_ches2007.pdf
# test vectors: http://www.crypto.ruhr-uni-bochum.de/imperia/md/content/texte/publications/conferences/slides/present_testvectors.zip

class Present:

        def __init__(self,key,rounds=32):
                """Generating roundkeys

                When a Present class is initialized, the roundkeys will be generated.
                You can supply the key as a 128-bit or 80-bit rawstring.
                """
                self.rounds = rounds
                if len(key) * 8 == 80:
                        self.roundkeys = generateRoundkeys80(string2number(key),self.rounds)
                elif len(key) * 8 == 128:
                        self.roundkeys = generateRoundkeys128(string2number(key),self.rounds)
                else:
                        raise ValueError, "Key must be a 128-bit or 80-bit rawstring"

        def encrypt(self,block):
                """Encrypting 1 block (8 bytes)

                Supply the plaintext block as a raw string and the raw
                ciphertext will be returned.
                """
                state = string2number(block)
                for i in range (1,self.rounds):
                        state = addRoundKey(state,self.roundkeys[i-1])
                        state = sBoxLayer(state)
                        state = pLayer(state)
                cipher = addRoundKey(state,self.roundkeys[self.rounds-1])
                return number2string_N(cipher,8)

        def decrypt(self,block):
                """Decrypting 1 block (8 bytes)

                Supply the ciphertext block as a raw string and the raw
                plaintext will be returned.
                """
                state = string2number(block)
                for i in range (1,self.rounds):
                        state = addRoundKey(state,self.roundkeys[self.rounds-i])
                        state = pLayer_dec(state)
                        state = sBoxLayer_dec(state)
                decipher = addRoundKey(state,self.roundkeys[0])
                return number2string_N(decipher,8)

        def get_block_size(self):
                return 8

#        0   1   2   3   4   5   6   7   8   9   a   b   c   d   e   f
Sbox= [0xc,0x5,0x6,0xb,0x9,0x0,0xa,0xd,0x3,0xe,0xf,0x8,0x4,0x7,0x1,0x2]
Sbox_inv = []
Sbox_inv.extend(Sbox.index(x) for x in range(16))
PBox = [0,16,32,48,1,17,33,49,2,18,34,50,3,19,35,51,
        4,20,36,52,5,21,37,53,6,22,38,54,7,23,39,55,
        8,24,40,56,9,25,41,57,10,26,42,58,11,27,43,59,
        12,28,44,60,13,29,45,61,14,30,46,62,15,31,47,63]
PBox_inv = []
PBox_inv.extend(PBox.index(x) for x in range(64))

def generateRoundkeys80(key,rounds):
        """Generate the roundkeys for a 80 bit key

        Give a 80bit hex string as input and get a list of roundkeys in return"""
        roundkeys = []
        for i in range(1,rounds+1): # (K1 ... K32)
                # rawkey: used in comments to show what happens at bitlevel
                # rawKey[0:64]
                roundkeys.append(key >>16)
                #1. Shift
                #rawKey[19:len(rawKey)]+rawKey[0:19]
                key = ((key & (2**19-1)) << 61) + (key >> 19)
                #2. SBox
                #rawKey[76:80] = S(rawKey[76:80])
                key = (Sbox[key >> 76] << 76)+(key & (2**76-1))
                #3. Salt
                #rawKey[15:20] ^ i
                key ^= (i & (2**5-1)) << 15
        return roundkeys

def generateRoundkeys128(key,rounds):
        """Generate the roundkeys for a 128 bit key

        Give a 128bit hex string as input and get a list of roundkeys in return"""
        roundkeys = []
        for i in range(1,rounds+1): # (K1 ... K32)
                # rawkey: used in comments to show what happens at bitlevel
                roundkeys.append(key >>64)
                #1. Shift
                key = ((key & (2**67-1)) << 61) + (key >> 67)
                #2. SBox
                key = (Sbox[key >> 124] << 124)+(Sbox[(key >> 120) & 0xF] << 120)+(key & (2**120-1))
                #3. Salt
                #rawKey[62:67] ^ i
                key ^= (i & (2**5-1)) << 62
        return roundkeys

def addRoundKey(state,roundkey):
        return state ^ roundkey

def sBoxLayer(state):
        """SBox function for encryption

        Takes a hex string as input and will output a hex string"""

        output = 0
        for i in range(0,16):
                output += Sbox[( state >> (i*4)) & 0xF] << (i*4)
        return output

def sBoxLayer_dec(state):
        """Inverse SBox function for decryption

        Takes a hex string as input and will output a hex string"""
        output = 0
        for i in range(0,16):
                output += Sbox_inv[(( state >> (i*4)) & 0xF)] << (i*4)
        return output

def pLayer(state):
        """Permutation layer for encryption

        Takes a 64bit hex string as input and will output a 64bit hex string"""
        output = 0
        for i in range(64):
                output += ((state >> i) & 0x01) << PBox[i]
        return output

def pLayer_dec(state):
        """Permutation layer for decryption

        Takes a 64bit hex string as input and will output a 64bit hex string"""
        output = 0
        for i in range(64):
                output += ((state >> i) & 0x01) << PBox_inv[i]
        return output

def bin(a):
        """Convert an integer to a bin string (1 char represents 1 bit)"""
        #http://wiki.python.org/moin/BitManipulation
        s=''
        t={'0':'000','1':'001','2':'010','3':'011','4':'100','5':'101','6':'110','7':'111'}
        for c in oct(a).rstrip('L')[1:]:
                s+=t[c]
        return s

def string2number(i):
    """ Convert a string to a number

    Input: string (big-endian)
    Output: long or integer
    """
    return int(i.encode('hex'),16)

def number2string_N(i, N):
    """Convert a number to a string of fixed size

    i: long or integer
    N: length of string
    Output: string (big-endian)
    """
    s = '%0*x' % (N*2, i)
    return s.decode('hex')
