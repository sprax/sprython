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
import random
import re
import string
from collections import defaultdict
from nltk.corpus import cmudict
import emoji
import emotuples

def syl_count_cmu(pron):
    '''number of syllables in a CMU-style pronunciation'''
    return sum(str.isdigit(syl[-1]) for syl in pron)

def syl_count_cmu_max(cmu_prons, word):
    '''
    Return the CMU syllable count for word (max if there are alternates),
    or KeyError.  The word should already be lowercased.
    '''
    prons = cmu_prons[word]
    return max(syl_count_cmu(pron) for pron in prons)

def syl_count_cmu_min(cmu_prons, word):
    '''
    Return the CMU syllable count for word (min if there are alternates),
    or KeyError.  The word should already be lowercased.
    '''
    prons = cmu_prons[word]
    return min(syl_count_cmu(pron) for pron in prons)

def syl_count_cmu_first(cmu_prons, word):
    '''
    Return the CMU syllable count for word (first if there are alternates),
    or KeyError.  The word should already be lowercased.
    '''
    first = cmu_prons[word][0]
    return syl_count_cmu(first)


EXAMPLES = {
    "There isn't one empyrean ouroborous; everyone knows there've always been several." : (11, 24),
    #  1   2  3  4   5  6 78   9 0 1  2   3 4* 5     6     7  8   9  0    1    2 3 4
    '"There aren\'t really any homogeneous cultures," you\'ll say, "they\'ve always shown rifts."' : (12, 21),
    #   1   2        3   5 6 7  8 9 0 1 2   3  4        5      6      7      8  9     0    1
    '"Ain\'t all y\'all young\'uns under 17," she\'d said, "like 11- or 15-years old?!"' : (13, 21),
    #  1     2      3    4     5   6  7  +3     1     2      3   +3  7  +2  0    1}
    "Didn't you know my X-15's XLR-99 engine burned 15,000 pounds (6,717 kg) of propellant in 87 seconds?" : (17, 35),
    # 1  2   3    4   5 6 +2    +3 +2 4  5    6     +2  +2  1     +3  +8 +3  6    7 8  9   0  +3  4 5
}


###############################################################################
WORD_SEP_INTERIOR = r"',.-"
RE_WORD_TOKEN = re.compile(r"((?:\w+[{}]\w*)+\w|\w+)".format(WORD_SEP_INTERIOR))

def word_tokens(sentence):
    return RE_WORD_TOKEN.findall(sentence)

###############################################################################
WORD_SEP_EXTERIOR = r'!"#$%&()*+./:;<=>?@[\]^_`{|}~\x82\x83\x84\x85\x86\x87\x88\x89' \
                    r'\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99'

RE_WORD_SEP = re.compile(r"(?:\s+[{}]+\s*|\s*[{}]+\s+|[{}]*[\s{}]+|\s+)".format(
    WORD_SEP_INTERIOR, WORD_SEP_INTERIOR, WORD_SEP_INTERIOR, WORD_SEP_EXTERIOR))

def word_splits(sentence):
    splits = RE_WORD_SEP.split(sentence)
    return [ss for ss in splits if len(ss) > 0]

###############################################################################
REGEX_PUNCTUATION = re.compile("[{}]".format(string.punctuation))
REGEX_NON_ALPHA = re.compile(r'(?:\W|[0-9])+')
###############################################################################

def qw(ss):
    return ss.split()

VOWEL_EXP = "ae|ai|au|ay|a|ea|ei|eu|ey|e|iou|ie|i|oa|oe|oi|ou|oy|o|ue|u|y|dn't|sn't"
VOWEL_GROUPS = VOWEL_EXP.split('|')
VOWEL_STR = ' '.join(VOWEL_GROUPS)

RE_VOWEL_GROUPS = re.compile("(?i)%s" % VOWEL_EXP)
# print('VOWEL_GROUPS: (', VOWEL_STR, ')\n')

def count_vowel_groups(word):
    '''crude dipthong & vowel count standing in for syllables'''
    vgm = RE_VOWEL_GROUPS.findall(word)
    # print("count_vowel_gp:", vgm)
    return len(vgm)

def count_vowels_first_last(word):
    '''naive rules to count syllables'''
    count = 0
    vowels = 'aeiouy'
    word = word.lower()
    oldc = word[0]
    if oldc in vowels:
        count += 1
    for nxtc in word[1:]:
        if nxtc in vowels and oldc not in vowels:
            count += 1
        oldc = nxtc
    if word.endswith('le'):
        count += 1
    elif word.endswith('e'):
        count -= 1
    if count == 0:
        count = 1
    return count


def syl_count(cmu_prons, word):
    '''
    syllable count: from the first CMU pronunciation, if found,
    or a calculated one.  The word should already be lowercased.
    '''
    try:
        return syl_count_cmu_first(cmu_prons, word)
    except KeyError:
        return count_vowel_groups(word)

def syl_count_sum(cmu_prons, words):
    '''sum of syllable counts for a sequence of lowercased words or tokens'''
    return sum(syl_count(cmu_prons, word) for word in words)


def syl_count_sentence(cmu_prons, sentence):
    '''sum of syllable counts for all tokens found in a sentence'''
    return syl_count_sum(cmu_prons, word_tokens(sentence))


def main():
    '''test english -> emoji translation'''
    parser = argparse.ArgumentParser(
        # usage='%(prog)s [options]',
        description="test english -> emoji translation")
    parser.add_argument('input_file', type=str, nargs='?', default='train_1000.label',
                        help='file containing text to filter')
    parser.add_argument('-dir', dest='text_dir', type=str, default='/Users/sprax/text',
                        help='directory to search for input_file')
    parser.add_argument('-charset', dest='charset', type=str, default='iso-8859-1',
                        help='charset encoding of input text')
    parser.add_argument('-output_file', type=str, nargs='?', default='lab.txt',
                        help='output path for filtered text (default: - <stdout>)')
    parser.add_argument('-verbose', type=int, nargs='?', const=1, default=1,
                        help='verbosity of output (default: 1)')
    args = parser.parse_args()
    # test_misc()

    cmu_prons = cmudict.dict() # get the CMU Pronouncing Dict

    for sentence, counts in EXAMPLES.items():
        print("MANUAL", counts[0], sentence)
        tokens = word_tokens(sentence)
        print("TOKENS", len(tokens), tokens)
        swords = word_splits(sentence)
        print("SPLITS", len(swords), swords)
        scount = syl_count_sum(cmu_prons, tokens)
        vcount = count_vowel_groups(sentence)
        fcount = count_vowels_first_last(sentence)
        print("SYLLABLES:  manual(%d)  cmupro(%d)  vowelg(%d)  nrules(%d)" % (
            counts[1], scount, vcount, fcount))
        print()


if __name__ == '__main__':
    main()