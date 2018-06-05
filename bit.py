from sys import stderr

BYTES_TYPE_I64: int = 64 / 8
BYTES_TYPE_I32: int = 32 / 8
BYTES_TYPE_I16: int = 16 / 8
BYTES_TYPE_I8:  int = 8 / 8


class BitfieldType:
    pass


def _get_type_by_bits(bits: int) -> int:
    if int(bits) is int((BYTES_TYPE_I64 * 8)):
        return BYTES_TYPE_I64
    if int(bits) is int((BYTES_TYPE_I32 * 8)):
        return BYTES_TYPE_I32
    if int(bits) is int((BYTES_TYPE_I16 * 8)):
        return BYTES_TYPE_I16
    if int(bits) is int((BYTES_TYPE_I8 * 8)):
        return BYTES_TYPE_I8

    return BYTES_TYPE_I8


def _get_type_by_num(num: int) -> int:
    bit_type = BYTES_TYPE_I8
    if num < -128 or num > 128:
        bit_type = BYTES_TYPE_I16
    if num < -32768 or num > 32767:
        bit_type = BYTES_TYPE_I32
    if num < -2147483648 or num > 2147483647:
        bit_type = BYTES_TYPE_I64

    return bit_type


def _get_unpack_mask_by_type(bit_type: int) -> int:
    mask: int = 0xFF000000000000
    if int(bit_type) is int(BYTES_TYPE_I64):
        return (mask ^ mask) | 0xFFFFFFFFFFFFFFFF
    if int(bit_type) is int(BYTES_TYPE_I32):
        return (mask ^ mask) | 0xFFFFFFFF00000000
    if int(bit_type) is int(BYTES_TYPE_I16):
        return (mask ^ mask) | 0xFFFF000000000000
    if int(bit_type) is int(BYTES_TYPE_I8):
        return (mask ^ mask) | 0xFF00000000000000

    return mask


def field(num: int) -> BitfieldType:
    pass


def set(num: int, index: int, state: bool) -> int:
    bit_type: int = _get_type_by_num(num)

    if index > (bit_type * 8):
        stderr.write('[PyBit]: Failed to set bit \'' + str(index) + '\' of \'' + str(num) + '\' '
                                            '(insufficient number of bits for specified index)\n')
        return -1

    if index <= 0:
        stderr.write('[PyBit]: Failed to set bit \'' + str(index) + '\' of \'' + str(num) + '\' '
                                            '(bit indices start at 1)\n')
        return -1

    bit_mask: int = 0b00000001 << (index - 1)
    if state:
        return num | bit_mask
    else:
        return num ^ bit_mask


def get(num: int, index: int) -> bool:
    bit_type: int = _get_type_by_num(num)
    if index > (bit_type * 8) or index <= 0:
        stderr.write('[PyBit]: Failed to get bit \'' + str(index) + '\' of \'' + str(num) + '\' '
                                            '(insufficient number of bits for specified index)\n')

    bit_mask: int = 0b00000001 << (index - 1)
    return (num & bit_mask) > 0


def cut(num: int, frm: int, to: int) -> int:
    bit_type: int = _get_type_by_num(num)

    if (frm > (bit_type * 8) or to > (bit_type * 8)) or frm >= to:
        stderr.write('[PyBit]: Failed to cut bit area from \'' + str(num) + '\''
                                            ' (\'from\' and/or \'to\' exceed the number of available bits)\n')
        return -1

    if frm <= 0 or to <= 0:
        stderr.write('[PyBit]: Failed to cut bit area from \'' + str(num) + '\' (bit indices start at 1)\n')
        return -1

    bit_mask: int = 0b000000001
    for n in range(to):
        bit_mask = bit_mask | (0b000000001 << n)

    return num & bit_mask


def pack(nums: list) -> int:
    packed: int = 0x0000000000000000

    shift: int = (BYTES_TYPE_I64 * 8)
    num_bits: int = 0x00
    for num in nums:
        if not isinstance(num, int):
            stderr.write('[PyBit]: Failed to pack \'' + str(nums) + '\' '
                                        '(one of the supplied values is not an integer)\n')
            return -1

        bit_type: int = _get_type_by_num(num)

        num_bits = num_bits + (bit_type * 8)
        if num_bits > (BYTES_TYPE_I64 * 8):
            stderr.write('[PyBit]: Failed to pack \'' + str(nums) + '\' '
                                        '(the sum of all bits within the given list is greater than 64)\n')
            return -1

        shift = shift - (bit_type * 8)
        packed = packed | (num << int(shift))

    return packed


def unpack(num: int, bit_format: list = []) -> list:
    if bit_format is None:
        bit_format = [8, 8, 8, 8, 8, 8, 8, 8]

    result = []
    shift: int = (BYTES_TYPE_I64 * 8)

    num_bits: int = 0x00
    for n in bit_format:
        if not isinstance(n, int):
            stderr.write('[PyBit]: Failed to unpack \'' + str(num) + '\' '
                                        '(one of the supplied values is not an integer)\n')
            return []

        num_bits = num_bits + n
        if num_bits > (BYTES_TYPE_I64 * 8):
            stderr.write('[PyBit]: Failed to unpack \'' + str(num) + '\' '
                                        '(the sum of all bits within the given list is greater than 64)\n')
            return []

        mask: int = _get_unpack_mask_by_type(_get_type_by_bits(n)) >> int(((BYTES_TYPE_I64 * 8) - shift))

        shift = shift - n
        result = result + [((num & mask) >> int(shift))]

    return result


def stringify(num: int) -> str:
    bit_type: int = _get_type_by_num(num)
    bits: int = int(bit_type * 8)

    builder: str = ""

    for n in range(bits):
        if (n % 8) == 0:
            builder = builder + " "

        bit_mask: int = 0b00000001 << n

        if (num & bit_mask) > 0:
            builder = builder + "1"
        else:
            builder = builder + "0"

    return builder[::-1]
