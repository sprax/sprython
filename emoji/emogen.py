#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# # # coding: iso-8859-15
'''
Plan:
    Words|phrases -> words >= [phonetic syllables reprs]
    Emojis >= [phontic syllable reprs]
    Text => <syllabic repr> => <emoji>
'''

import argparse
import emoji
import re
from collections import defaultdict
import emotuples as ed
import emotrans as et
import sylcount as sylc
from nltk.corpus import cmudict

def gen_emo_tuples():
    old_emos = ed.EmoTuples.emo_tuples

EX = [ ('1f602',  7, 1, 1, '😂', ['joy', 'happy'], ':joy:', [], [], 'people') ,
       ('1f923',  8, 0, 1, '\U0001f923', ['rofl'], ':rofl:', [':rolling_on_the_floor_laughing:'], [], 'people') ,
       ( '263a',  9, 1, 1, '☺', ['relaxed', 'relax', 'chill'], ':relaxed:', [], [], 'people') , ]

def regen_emo_tuples(name='EMO_TUPLES', start=None, stop=None, incr=None):
    cmu_prons = cmudict.dict() # get the CMU Pronouncing Dict
    print(name, "= [")
    if stop == 0:
        stop = None
    for t in ed.EMO_TUPLES[start:stop:incr]:
        monos, polys = set(), set()
        for word in t[5]:
            if sylc.syl_count(cmu_prons, word) == 1:
                monos.add(word)
            else:
                polys.add(word)
        shorts = sylc.word_splits(t[6])
        for short in shorts:
            if sylc.syl_count(cmu_prons, short) == 1 and short not in monos:
                monos.add(short)
            else:
                polys.add(short)
        # print("shorts: {}  monos: {}  polys: {}  alts: {}".format(shorts, monos, polys, t[7]))
        lst = list(t[0:4])
        lst.extend([et.unicode_chr_str(t[0]), list(monos), t[6], t[7], list(polys), t[9]])
        print("    {},".format(tuple(lst)))
    print("]")

DICT_COLS = ('order', 'flags', 'len', 'chr', 'monosyls', 'shortname', 'alternates', 'polysyls', 'category')
COL_TO_IDX = dict([(v, i) for i, v in enumerate(DICT_COLS)])

def emo_value_col(value, column):
    return value[COL_TO_IDX(column)]

def emo_dict_col(emodict, key, column):
    return emo_value_col(emodict[key], column)

def gen_emo_dict(name='EMO_DICT', start=None, stop=None, incr=None):
    print(name, "= {")
    for t in ed.EMO_TUPLES[start:stop:incr]:
        print("    '%s' : %s," % (t[0], t[1:4] + (et.unicode_chr_str(t[0]),) + t[5:]))
    print("}")


def main():
    parser = argparse.ArgumentParser(
        # usage='%(prog)s [options]',
        description="generate some maps for english -> emoji translation")
    parser.add_argument('input_file', type=str, nargs='?', default='train_1000.label',
                        help='file containing text to filter')
    parser.add_argument('-charset', dest='charset', type=str, default='iso-8859-1',
                        help='charset encoding of input text')
    parser.add_argument('-output_file', type=str, nargs='?', default='lab.txt',
                        help='output path for filtered text (default: - <stdout>)')
    parser.add_argument('-beg', type=int, nargs='?', const=0, default=6,
                        help='starting index')
    parser.add_argument('-end', type=int, nargs='?', const=0, default=12,
                        help='ending index')
    parser.add_argument('-verbose', type=int, nargs='?', const=1, default=1,
                        help='verbosity of output (default: 1)')
    args = parser.parse_args()

    # gen_emo_dict('EMO_DICT', args.beg, args.end)
    print("col_to_idx:", sorted(COL_TO_IDX, key=COL_TO_IDX.get))
    regen_emo_tuples('EMO_TUPLES', args.beg, args.end)

if __name__ == '__main__':
    main()