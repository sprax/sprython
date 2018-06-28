#!/usr/bin/env python3
''' tests for various palindromes using Python 3 generators
    Python 2.7 *can* run this version.
'''

from __future__ import print_function
import argparse
import sys
# import pdb
# from pdb import set_trace

def _sup_palindromic_num_str(num_str):
    '''
    returns the supremum palindrome of the num in num_str, that is,
    the least palindromic number greater than or equal to num.
    Thus it returns num IFF num_str is already a palindrome.
    '''
    assert(isinstance(num_str, str))
    raise NotImplementedError("Not Yet Implemented for value %d > 32" % num)


def gen_palindromic_nums(num):
    '''case-based generation of next (greater) palindromic integer'''
    raise NotImplementedError("Not Yet Implemented for num == %d" % num)


def init_counter(count=0):
    '''(re)set counter that increments whenever called (closure)'''
    _count_dict = { 'count' : count }       # put the enclosed value in a dict
    def _increment_counter():               # to avoid rebinding (for Python 2)
        '''inner incrementer function'''
        _count_dict['count'] += 1
        return _count_dict['count']
    return _increment_counter


NUM = 0
def gen_even():
    '''yield all even natural numbers'''
    global NUM
    while True:
        NUM += 2
        yield num


def is_palindrome_slice(string):
    '''true IFF palindrome'''
    half_len = len(string) // 2
    for lef, rig in zip(string[0:half_len+1], string[-1:half_len-1:-1]):
        if lef != rig:
            return False
    return True

def is_chunky_palindrome(string):
    '''
    true IFF palindrome in chunks, as in:
    volvo -> (vo)l(vo)
    oliverelivo -> (o)(liv)(e)(r)(e)(liv)(o)
    Greedy algorithm should succeed.
    '''
    half_len = len(string) // 2
    beg = 0
    while beg < half_len:
        end = -1 - beg
        if string[beg] != string[end]:
            end = None if end == -1 else end + 1
            for med in range(beg+2, half_len+1):
                if string[beg:med] == string[-med:end]:
                    beg = med
                    break
            else:
                return False
        else:
            beg += 1
    return True



def test_one_string(is_palindrome, expect, verbose, string):
    '''
    tests the is_palindrome function on one string.
    Returns the number of wrong answers, that is,
    0 if is_palindrome matches expect,
    1 if it does not.
    '''
    is_pal = is_palindrome(string)
    passed = is_pal == expect
    if verbose > passed:
        print("%s %s: expected %s: %s %s" % (is_palindrome.__name__,
                                             "PASS" if passed else "FAIL",
                                             expect,
                                             " "*(24 - len(string)),
                                             " ".join(string)))
    return not passed


def test_is_palindrome(is_palindrome, expect_string_pairs, verbose=0):
    ''' tests an is_palindrome function and returns the number of wrong answers'''
    num_wrong = 0
    for expect, string in expect_string_pairs:
        num_wrong += test_one_string(is_palindrome, expect, verbose, string)
    return num_wrong

def unit_test(args):
    ''' test different (kinds of) palindrome detectors '''
    verbose = args.verbose
    expect_string_pairs = [
        [0, "volvo"],
        [0, "oliverelivo"],
        [1, "volvovlov"],
        [0, "XO"],
        [1, "ZZ"],
        [1, "XOX"],
    ]
    num_wrong = 0
    num_wrong += test_is_palindrome(is_palindrome_range, expect_string_pairs, verbose)
    num_wrong += test_is_palindrome(is_palindrome_slice, expect_string_pairs, verbose)
    expect_string_pairs[1][0] = expect_string_pairs[0][0] = 1
    num_wrong += test_is_palindrome(is_chunky_palindrome, expect_string_pairs, verbose)
    print("END palindromes.unit_test:  num_wrong: %d" % num_wrong)


def even_fib_gen():
    a,b = 1,2
    while True:
        yield b
        a,b = a+2*b, 2*a+3*b


def next_palindromic_num(num):
    '''Given an integral num, compute the next palindromic number (strictly
    greater than num) using only arithmetic operations.
    TODO: eliminate the string conversion entirely; we only want the number of
    digits in canonical form.
    TODO: better argument checking?
    '''
    num = int(num)  # Try to convert arg to int.  TODO: Raise on any non-integral arg?
    if num < 0:     # Negative numbers are not palindromes due to the "-"
        return 0
    if num < 9:
        return num + 1
    if num < 11:
        return 11
    num += 1
    # print("num %d incremented to %d" % (num-1, num))
    num_str = str(num)
    num_len = len(num_str)
    lef_den = 10 ** (num_len - 1)
    rig_den = 1
    haf_len = num_len // 2
    evn_max = (num_len + 1) // 2 - 1
    for idx in range(haf_len):
        lef_dig = (num // lef_den) % 10
        rig_dig = (num // rig_den) % 10
        # print("\nidx %d,  num %d: lef_dig, rig_dig == (%d, %d)" % (idx, num, lef_dig, rig_dig))
        if  lef_dig > rig_dig:
            # print("simple: lef_dig %d > %d rig_dig" % (lef_dig, rig_dig))
            num += (lef_dig - rig_dig)*rig_den
        elif lef_dig < rig_dig:
            add_num = num + rig_den*10
            nxt_dec = (num / lef_den + 1) * lef_den # a.k.a. lef_dig + 1) * lef_den)
            # print("add_num == num + rig_den*10 = %d + %d*%d = %d" % (num, rig_den, 10, add_num))
            # print("        >? (%d / %d + 1) * %d = %d * %d = %d" % (num, lef_den, lef_den, num/lef_den + 1, lef_den, nxt_dec))
            if add_num > nxt_dec:
                # print("----- carry numbers -----  num %d -> %d > %d   " % (num, add_num, nxt_dec))
                num += rig_den*10 + rig_den*(1 + lef_dig - rig_dig)
            else:
                # print("---- no carry ----")
                num += rig_den*10 + rig_den*(lef_dig - rig_dig)
        lef_den /= 10
        rig_den *= 10
    return  num


def main():
    '''drive tests of number generators'''
    parser = argparse.ArgumentParser(description=unit_test.__doc__)
    parser.add_argument('-verbose', type=int, nargs='?', const=1, default=1,
                        help='verbosity of output (default: 1)')
    args = parser.parse_args()
    vinfo = sys.version_info
    v_major = vinfo[0]
    v_minor = vinfo[1]
    ver_str = "Python %d.%d" % (v_major, v_minor)
    print(ver_str)

    even_fibs = even_fib_gen()
    print("next(even_fibs) yields: %4d" % next(even_fibs))
    print("next(even_fibs) yields: %4d" % next(even_fibs))
    # print("Python %s: next(even_fibs) yields: %d" % (ver_str, next(even_fibs)))
    # print("Python %s: next(even_fibs) yields: %d" % (ver_str, next(even_fibs)))
    # print("Python %s: next(even_fibs) yields: %d" % (ver_str, next(even_fibs)))
    # if v_major < 3:
    #     raise Exception("Call this script with Python 3")
    for idx, num in enumerate(even_fib_gen()):
        if idx > 12:
            break;
        print("for-loop:  %2d  %30d" % (idx, num))
    # unit_test(args)



if __name__ == '__main__':
    main()