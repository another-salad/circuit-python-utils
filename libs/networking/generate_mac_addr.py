"""Generates a random mac address in the Raspi foundation range."""

import random


def gen_mac_addr():
    """Generates a mac address"""
    rand_part = lambda: f"0x{random.randint(0, 255):02x}"
    return f"0xdc:0xa6:0x32:{rand_part()}:{rand_part()}:{rand_part()}"


if __name__ == "__main__":
    print(gen_mac_addr())
