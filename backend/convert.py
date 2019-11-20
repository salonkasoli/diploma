import binascii

def str_to_number(s):
    number = int(binascii.hexlify(s.encode('utf-8')), 16)
    return number
    
def number_to_str(number):
    hx = '%x' % number
    hx = hx.zfill(len(hx) + (len(hx) & 1))  # Make even length hex nibbles
    recoveredstring = binascii.unhexlify(hx).decode('utf-8')
    return recoveredstring
