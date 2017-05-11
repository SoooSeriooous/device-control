__author__ = 'pronin_v'


def generate_cs(checkword):
    magic_number = 65535
    for i in range(1, len(checkword)):
        magic_number ^= ord(checkword[i])
        for j in range(8):
            if (magic_number/2)*2 != magic_number:
                magic_number = (magic_number/2) ^ 40961
            else:
                magic_number /= 2
    return str(magic_number)
