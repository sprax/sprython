#!/usr/bin/env python3
r'''
Find the clustered sequences of indices of characters in a string S that match
those of a given search string T, in-order but not necessarily contiguously.
location of BCD in String S. 
Given for example S = BCXXBXXCXDXBCD and T = BCD, then the result should be [[4,7,9],[11,12,13] 
Given T = BCBC and String S = BCXXBXCXBCBC, the result should be [[0,1,4,6],[8,9,10,11]]
'''
from __future__ import print_function

import argparse
# import pdb
# from pdb import set_trace
# import random
# import re


def sub_str_idxs(seq_str, sub_str):
    ''' test sub-sequences (or non-contiguous embedded string indices) stuff
    Given for example S = BCXXBXXCXDXBCD, then the result should be [[4,7,9],[11,12,13] 
    '''
    result = []
    sub_res = []
    len_sub = len(sub_str)
    if seq_str and sub_str:
        sub_idx = 0
        nxt_chr = sub_str[sub_idx]
        for seq_idx, seq_chr in enumerate(seq_str):
            if seq_chr == nxt_chr:
                sub_res.append(seq_idx)
                if len(sub_res) == len_sub:
                    result.append(sub_res) 
                    sub_res = []
                    sub_idx = 0
                else:
                    sub_idx += 1
                    nxt_chr = sub_str[sub_idx]
            elif seq_chr in sub_str:
                sub_res = []
                sub_idx = 0
    return result

def unit_test(args):
    ''' test sub-sequences (or non-contiguous embedded string indices) stuff '''
    result = sub_str_idxs("BCXXBXXCXDXBCD", "BCD")
    print("The result should be [[4,7,9],[11,12,13]]")
    print("The actual result is ", result) 

def main():
    '''driver for unit_test'''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-verbose', type=int, nargs='?', const=2, default=1,
                        help='verbosity of output (const=2, default: 1)')
    args = parser.parse_args()

    unit_test(args)


if __name__ == '__main__':
    main()
