# funkcje pomocnicze

def XOR(bits1, bits2):
    return ''.join('0' if b1 == b2 else '1' for b1, b2 in zip(bits1, bits2))


get_bin = lambda x, n=5: format(x, 'b').zfill(n)


def apply_permutation(bits, table):
    return ''.join(bits[idx - 1] for idx in table)


def str_to_binary(s):
    return ''.join(get_bin(ord(c), 8) for c in s)


def bin_to_str(bits):
    return ''.join([chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8)])


# wyznaczanie kluczy rund

def shift_bits(bits, shift):
    s = len(bits) // 2 - shift // 2
    t = s + shift

    first_bits = bits[:s]

    if shift % 3 != 1:
        first_bits = ''.join(reversed(bits[:s]))

    middle_bits = bits[s:t]

    if shift % 2 == 1:
        middle_bits = ''.join(reversed(bits[s:t]))

    return bits[t:] + middle_bits + first_bits


def key_64_bits_to_60_bits(key_64_bits):
    t = [31, 3, 41, 32, 49,
         21, 30, 55, 9, 37,
         50, 51, 12, 60, 20,
         62, 1, 7, 23, 36,
         27, 2, 28, 29, 6,
         64, 10, 56, 19, 8,
         63, 17, 24, 35, 43,
         59, 53, 46, 39, 22,
         48, 18, 25, 40, 47,
         15, 54, 44, 45, 34,
         61, 58, 16, 11, 5,
         14, 26, 57, 33, 38]

    return apply_permutation(key_64_bits, t)


def split_60_bits_in_5(key_60_bits):
    return [key_60_bits[i * 12: (i + 1) * 12] for i in range(0, 5)]


def key_12_to_7_bits(key_12_bits):
    t = [8, 6, 11, 12, 1, 3, 9]
    return apply_permutation(key_12_bits, t)


def generate_13_keys_35_bits(key_64_bits):
    shifts = [1, 3, 2, 1, 2, 4, 2, 3, 1, 2, 2, 4, 1]

    key_60_bits = key_64_bits_to_60_bits(key_64_bits)

    round_keys = [str()] * len(shifts)
    split = split_60_bits_in_5(key_60_bits)

    for i, shift in enumerate(shifts):
        split = [shift_bits(bits, shift) for bits in split]

        round_keys[i] = ''.join([key_12_to_7_bits(bits) for bits in split])

    return round_keys


# funkcja f


SBOX = [
    [[2, 15, 14, 11, 4, 1, 8, 13],
     [13, 1, 6, 8, 14, 4, 2, 11],
     [2, 7, 9, 15, 8, 4, 12, 1],
     [13, 7, 1, 14, 2, 15, 0, 4]],

    [[1, 3, 8, 4, 11, 15, 14, 6],
     [1, 2, 8, 15, 10, 4, 13, 3],
     [0, 13, 11, 14, 1, 4, 7, 10],
     [7, 13, 2, 8, 14, 3, 4, 15]],

    [[5, 0, 9, 14, 6, 10, 15, 3],
     [8, 9, 10, 7, 6, 1, 13, 0],
     [13, 8, 9, 15, 6, 4, 0, 3],
     [0, 7, 6, 4, 10, 3, 9, 13]],

    [[9, 13, 12, 11, 0, 7, 6, 10],
     [14, 0, 4, 3, 7, 13, 6, 9],
     [6, 10, 0, 13, 3, 8, 15, 1],
     [11, 6, 8, 0, 13, 15, 3, 5]],

    [[2, 7, 12, 14, 8, 11, 13, 1],
     [12, 1, 10, 6, 2, 11, 7, 4],
     [4, 13, 11, 2, 1, 7, 14, 12],
     [11, 7, 8, 4, 13, 2, 10, 1]],

    [[15, 12, 2, 5, 4, 3, 10, 9],
     [12, 8, 1, 15, 6, 10, 9, 2],
     [9, 3, 15, 14, 8, 5, 2, 12],
     [10, 4, 5, 15, 9, 12, 7, 2]],

    [[10, 8, 11, 7, 1, 4, 6, 13],
     [11, 4, 2, 15, 0, 13, 8, 14],
     [7, 0, 4, 9, 13, 11, 10, 1],
     [13, 7, 12, 4, 1, 3, 11, 3]]

]


def sbox_get(i, bits5):
    row = int(bits5[1] + bits5[3], base=2)
    col = int(bits5[0] + bits5[2] + bits5[4], base=2)
    return get_bin(SBOX[i][row][col])


def expand_28_to_35(bits28):
    t = [9, 14, 26, 22, 6,
         17, 5, 15, 10, 3,
         25, 11, 4, 28, 12,
         8, 1, 18, 3, 12,
         23, 2, 20, 21, 25,
         17, 16, 19, 24, 21,
         13, 14, 7, 27, 6]

    return apply_permutation(bits28, t)


def split_35_in_5(bits35):
    return [bits35[i: i + 5] for i in range(0, 35, 5)]


def functionF(pre28bits, key35bits):
    expanded = expand_28_to_35(pre28bits)

    xor_ed = XOR(expanded, key35bits)

    bits5 = split_35_in_5(xor_ed)

    final28bits = ''.join(sbox_get(i, bits) for i, bits in enumerate(bits5))

    return final28bits


# glowny algorytm

def split_56_in_2(bits_56):
    return bits_56[:28], bits_56[28:]


def encrypt_56_bits(message_56_bits, key_64_bits):
    round_keys = generate_13_keys_35_bits(key_64_bits)

    l, r = split_56_in_2(message_56_bits)

    for key in round_keys:
        l, r = r, XOR(l, functionF(r, key))

    return l + r


def decrypt_56_bits(message_56_bits, key_64_bits):
    round_keys = generate_13_keys_35_bits(key_64_bits)

    l, r = split_56_in_2(message_56_bits)

    for key in reversed(round_keys):
        l, r = XOR(r, functionF(l, key)), l

    return l + r


# prezentacja działania

def print_test(plain_key, plain_text):
    key_64bits = str_to_binary(plain_key)[:64]
    bits = str_to_binary(plain_text)[:56]

    if len(key_64bits) != 64:
        print("wrong key")
        return

    if len(bits) != 56:
        print("wrong plain text")
        return

    print(f"   plain text   : {plain_text}")
    print(f"     bits       : {bits}")
    encrypted = encrypt_56_bits(bits, key_64bits)
    print(f"   encrypted    : {encrypted}")
    decrypted = decrypt_56_bits(encrypted, key_64bits)
    print(f"   decrypted    : {decrypted}")
    print(f"plain decrypted : {bin_to_str(decrypted)}")
    print()


def test1():
    plain_key = 'get ready!'
    plain = 'attack!'

    print_test(plain_key, plain)


def test2():
    plain = 'crypto-'
    plain_key = 'is fun!!!'

    print_test(plain_key, plain)


if __name__ == '__main__':
    test1()
    test2()
