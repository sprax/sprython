#!/usr/bin/env python3
# Sprax Lines       2016.09.01      Written with Python 3.5
'''Extract doubly-quoted strings from a file of paragraphs'''

import heapq
import itertools
import re
import sys
from collections import defaultdict
from collections import Counter

import utf_print

def paragraphs(fileobj, separator='\n'):
    """Iterate a fileobject by paragraph"""
    ## Makes no assumptions about the encoding used in the file
    lines = []
    for line in fileobj:
        if line == separator and lines:
            yield ' '.join(lines)
            lines = []
        else:
            lines.append(line)
    yield ' '.join(lines)

def paragraphs_re(fileobj, separator='\n'):
    """Iterate a fileobject by paragraph"""
    ## Makes no assumptions about the encoding used in the file
    lines = []
    for line in fileobj:
        if re.match(separator, line) and lines:
            yield ' '.join(lines)
            lines = []
        else:
            line = line.rstrip().replace('’', "'")
            if line:
               lines.append(line)
    yield ' '.join(lines)


def print_paragraphs(path):
    print("print_paragraphs:")
    with open(path) as f:
        for idx, para in enumerate(paragraphs_re(f)):
            print("    Paragraph {}:".format(idx))
            print(para)
            print()


def find_quoted_replies(path, verbose):
    '''Finds first 3 (or fewer) words starting quoted replies.
       Returns a defaultdict mapping these phrases to their counts.
       Words longer than 1-letter are lowercased.'''
    rgx_quoted_B = re.compile(r'(["])(?:(?=(\\?))\2.)*?\1')
    rgx_quoted_A = re.compile(r'([^"]+)')
    rgx_quoted = re.compile(r'"([^"]*)"')
    rgx_word = re.compile(r"[A-Z'’a-z]+")
    rgx_para_numbering = re.compile(r"^[^A-Za-z]*(\d|[ivx]+\.)")
    reply_counter = Counter()
    denial_counter = Counter()
    idx = 0
    with open(path, 'r', encoding="utf8") as text:
        for para in paragraphs_re(text):
            if re.match(rgx_para_numbering, para):
                continue
            quotes = re.findall(rgx_quoted, para)
            phrases = []
            is_denial = False
            for quote in quotes:
                if verbose > 3:
                    print("quote {}: {}".format(idx, quote))
                idx += 1
                phrase = []
                words = re.findall(rgx_word, quote)
                for word in words[:3]:
                    if len(word) == 1:
                        phrase.append(word)
                    else:
                        low = word.lower()
                        phrase.append(low)
                        if low == "no" or low == "not" or low == "don't":
                            is_denial = True
                if phrase:
                    joined = ' '.join(phrase)
                    is_question = is_question_word(phrase[0])
                    if is_denial and not is_question:
                        is_denial = False
                        denial_counter.update([joined])
                    phrases.append(joined)
            reply_counter.update(phrases)
            ## for ppp in phrases:
            ##    print("ppp: ", ppp)
    return reply_counter, denial_counter

def main():
    '''Get file names for cipher and corpus texts and call
    find_quoted_no_phrases.'''


    # simple, inflexible arg parsing:
    argc = len(sys.argv)
    if argc > 4:
        print(sys.argv[0])
        print(__doc__)
        exit(0)

    # Get the paths to the files (relative or absolute)
    adverb_file = sys.argv[1] if argc > 1 else r'adverb.txt'
    corpus_file = sys.argv[2] if argc > 2 else r'corpus.txt'
    verbose = int(sys.argv[3]) if argc > 3 else 3

    find_quoted_no_phrases(adverb_file, corpus_file, verbose)


if __name__ == '__main__':
    main()
