#!/usr/bin/env python3
# Note: do not use Latin-1 encoding, because it would force string
# literals to use byte encoding, which results in unicode characters > 255
# being ignored in regular expression strings.
# That is, do NOT put the following on the first or second line: -*- coding: latin-1 -*-
#
#
# Sprax Lines       2016.09.01      Written with Python 3.5
'''Common operations for textual corpora, including:
   * File readers that yield one paragraph at a time.
   * Frequency-based word filtering.
'''

# from string import punctuation
import argparse
import math
import re
import sys
from collections import defaultdict, namedtuple

from utf_print import utf_print

INF_NUM_WORDS = 2**30

RE_PARA_SEPARATOR = re.compile(r'\s*\n')

################################################################################

def paragraph_iter(fileobj, rgx_para_separator=RE_PARA_SEPARATOR, sep_lines=0):
    r'''
    yields paragraphs from text file and regex separator, which by default matches
    one blank line (only space before a newline, or r"\s*\n").  All but the first
    paragraph will begin with the separator, unless it contains only whitespace,
    which is stripped from the end of every line.
    TODO: Consider adding span-matching for square brackets, that is, never
    breaking a paragraph on text between an open bracket [ and a matching, i.e.
    balance end bracket ].  Likewise { no break between curly braces }.
    '''
    ## Makes no assumptions about the encoding used in the file
    paragraph, blank_lines = '', 0
    for line in fileobj:
        #print("    PI: line(%s) para(%s)" % (line.rstrip(), paragraph))
        if re.match(rgx_para_separator, line) and paragraph and blank_lines >= sep_lines:
            yield paragraph
            paragraph, blank_lines = '', 0
        line = line.rstrip()
        if line:
            blank_lines = 0
            if not paragraph:
                paragraph = line
            elif paragraph.endswith('-'):
                paragraph += line
            else:
                paragraph += ' ' + line
        else:
            blank_lines += 1
    if paragraph:
        yield paragraph

def is_blank_line(line):
    for char in line:
        if char != ' ' and char != '\t' and char != '\n' and char != '\r':
            return False
    return True

REC_BLANK_LINE = re.compile(r'^\s*$')

def is_blank_line_re(line):
    return REC_BLANK_LINE.match(line)

REC_WORDY = re.compile(r'\w+')

def is_wordy_re(line):
    return REC_WORDY.search(line)



################################################################################
def lex_entry_ns_iter(fileobj, rgx_para_separator=RE_PARA_SEPARATOR, sep_lines=0):
    '''
    Yields paragraphs (including newlines) representing lexion entries from a text
    file and regex separator, which by default matches a blank line followed by an
    all-uppercase word.  The all-caps word is included in the paragraph, as are any
    newlines upto the next paragraph separator.  In general, lines are not stripped
    of whitespace.
    TODO: stop counting blank_lines and entry_lines.
    '''
    ## Makes no assumptions about the encoding used in the file
    paragraph, blank_lines, entry_lines = '', 0, 0
    for line in fileobj:
        #print("    PI: line(%s) para(%s)" % (line.rstrip(), paragraph))
        if re.match(rgx_para_separator, line) and paragraph and blank_lines >= sep_lines:
            yield paragraph
            paragraph, blank_lines, entry_lines = '', 0, 0
        if is_blank_line(line):
            if paragraph:
                paragraph += "\n"
                entry_lines += 1
            blank_lines += 1
        else:
            blank_lines = 0
            if paragraph:
                paragraph += line
                entry_lines += 1
            else:
                paragraph = line
                entry_lines = 1
    if paragraph:
        yield paragraph

def paragraph_multiline_iter(fileobj, rgx_para_separator=r'\s*\n\s*\n\s*|\s*\n\t\s*'):
    '''yields paragraphs from text file and regex separator, which by default matches
    one or more blank lines (two line feeds among whitespace),
    or one line-feed followed by a tab, possibly in the middle of other whitespace.'''
    ## Makes no assumptions about the encoding used in the file
    paragraph = ''
    for line in fileobj:
        if re.match(rgx_para_separator, line) and paragraph:
            yield paragraph
            paragraph = ''
        else:
            line = line.rstrip()
            if line:
                if paragraph.endswith('-'):
                    paragraph += line
                else:
                    paragraph += ' ' + line
    if paragraph:
        yield paragraph

def paragraph_reader(path, charset="utf8", rgx_para_separator=RE_PARA_SEPARATOR):
    '''opens text file and returns paragraph iterator'''
    try:
        text_stream = open(path, 'r', encoding=charset)
        return paragraph_iter(text_stream, rgx_para_separator), text_stream
    except FileNotFoundError as ex:
        print("Warning:", ex)
        return None, None

def para_iter_file(path, rgx_para_separator=RE_PARA_SEPARATOR, sep_lines=0, charset='utf8'):
    '''Generator yielding filtered paragraphs from a text file'''
    # print("para_iter_file: pattern: %s" % rgx_para_separator.pattern)
    with open(path, 'r', encoding=charset) as text:
        for para in paragraph_iter(text, rgx_para_separator, sep_lines):
            yield para

###############################################################################
REP_UPPER_WORD = r'^\s*([A-Z-]+)\b\s*'
REC_UPPER_WORD = re.compile(REP_UPPER_WORD)

def para_ns_iter_lex_file(path, rgx_para_separator=REC_UPPER_WORD, sep_lines=0, charset='utf8'):
    '''Generator yielding filtered paragraphs (including newlines) from a lexicon file'''
    # print("para_ns_iter_lex_file: pattern: %s" % rgx_para_separator.pattern)
    with open(path, 'r', encoding=charset) as text:
        for para in lex_entry_ns_iter(text, rgx_para_separator, sep_lines):
            yield para

def put(*args, sep=''):
    print(*args, sep=sep)

REC_FIRST_WORD_TOKEN = re.compile(r'^(-?\w+|\W*\w+-?)')

def first_token(text, default=None):
    '''return the first word-like token parsed from a string'''
    try:
        return REC_FIRST_WORD_TOKEN.match(text).groups()[0]
    except AttributeError:
        return default

def print_groups(match):
    '''print groups from a regex match'''
    if match:
        for grp in match.groups():
            print("  {}".format(grp))

# REP_WEBSTER1 = r'\n([A-Z-]+)\s+([^\s,]+)[^,]*,\s+((?:[a-z]\.\s*)+)'\
#                 '(?:Etym:\s+\[([^]]+)\])?\s*(?:Defn:\s)([^.]+)?'
# REP_WEBSTER = r"([A-Z'-]+)\s+([^\s,]+)[^,]*,\s+((?:[a-z]\.\s*)+)"\
#                "(?:Etym:\s+\[([^]]+)\])?\s*(?:Defn:\s+)?((?:[^.]+.\s+)*)"
#
# REP_SPC = r'[\s.,]+'
# REP_WEBSTER = r'([A-Z-]+)\s+([^\s\(\[,]+)\s*(\([^(]+\))?(\[[^\]]+\])?([^,]*,?)\s+'\
#                '((?:[a-z]\.\s*)+)?(?:Etym:\s+\[([^]]+)\])?\s*(?:Defn:\s+)?((?:[^.]+.\s+)*)'
# REC_WEBSTER = re.compile(REP_WEBSTER)


EXAMPLE = "BACE Bace, n., a., & v."

REP_PART = r'a|adv|conj|i|imp|interj|n|p|prep|t|v'


# FIXME TODO: Two passes:
# First pass regex to detect the number of words:
#   a) how many variants (word_1, word_2, etc., e.g. IMAM; IMAN; IMAUM)
#   b) how many words in each variant (e.g. BANK BILL, ICELAND MOSS)
# Second pass regex depends on what's found in the first pass.
REC_WEBSTER = re.compile(r"""
    ^(?P<word_1>(?:[A-Z]+['-]?\ ?)+[A-Z]+['-]?\b|[A-Z]+['-]?|[A-Z\ '-]+) # Primary WORD and whitespace
    (?:;\s+(?P<word_2>[A-Z'-]+))?                   # WORD 2 (variant spelling)
    (?:;\s+(?P<word_3>[A-Z'-]+))?\t\                # WORD 3 (variant spelling)
    (?P<pron_1>[A-Z](?:\w*['"*-]?\ ?)+\w+['"*-]?|[A-Z]\w*[^\s\(\[.,]+|[A-Z]\w+\s(?!Defn)\w+|-\w+) # Pron 1 (Capitalized)
    (?:,\s*(?P<pron_2>[A-Z][^\s\(\[,.]+))?          # Pronunciation 2 (for variant 2)
    (?:,\s*(?P<pron_3>[A-Z][^\s\(\[,.]+))?[\s.,]+   # Pronunciation 3 (for variant 2)
    (?:\s*\((?P<pren1a>[^\)]+)\)\s*)?               # parenthesized 1a
    (?:,?\s*(?P<part1a>(?:(?:{})\s*\.\s*)+))?       # part of speech for first definition (order varies)
    (?:\s*;\s+pl\.\s+(?P<plural>[\w-]+))?           # plural form or suffix, usually for irregulars
    (?:\s*\((?P<pren1b>[^\)]+)\)\s*)?               # parenthesized 1b
    (?:\.?\s*\[(?P<brack1>[^\]]+)\]\s*)?            # bracketed
    (?P<sepsp1>[\s.,]*?)                      # non-greedy space, punctuation(period, comma)
    (?:\s*(?P<part1b>(?:(?:{})\s*\.\s*)+))?   # part of speech for first definition (order varies)
    (?:Etym:\s*\[(?P<etym_1>[^\]]+)\]\s*)?    # etymology
    (?:\((?P<dtype1>[A-Z][\w\s&]+\.)\)\s*)?   # subject field abbreviations, e.g. (Arch., Bot. & Zool.)
    (?:(?P<dftag1>Defn:|1\.|\(a\))\s+\.?\s*(?P<defn_1>[^.]+\.))?\s*   # Defn 1 tag and first sentence of definition.
    (?P<defn1a>[A-Z][^.]+\.)?\s*              # definition 1 sentence 2
    (?:;)?\s*                                 # optional separator
    (?P<usage1>".*"[^\d]+)?\s*                # example 1
    (?P<defn_2>\d.\s[^\d]+)?                  # definition 2, ...
    (?P<cetera>.*)?$                          # etc.
""".format(REP_PART, REP_PART), re.VERBOSE)

REC_PARTIAL = re.compile(r"""
    ^(?P<word_1>(?:[A-Z]+['-]?\ ?)+[A-Z]+['-]?\b|[A-Z]+['-]?|[A-Z\ '-]+) # Primary WORD and whitespace
    (?:;\s+(?P<word_2>[A-Z'-]+))?                   # WORD 2 (variant spelling)
    (?:;\s+(?P<word_3>[A-Z'-]+))?\n                 # WORD 3 (variant spelling)
    (?P<pron_1>[A-Z](?:\w*['"*-]?\ ?)+\w+['"*-]?|[A-Z]\w*[^\s\(\[.,]+|[A-Z]\w+\s(?!Defn)\w+|-\w+) # Pron 1 (Capitalized)
    (?:,\s*(?P<pron_2>[A-Z][^\s\(\[,.]+))?          # Pronunciation 2 (for variant 2)
    (?:,\s*(?P<pron_3>[A-Z][^\s\(\[,.]+))?[\s.,]+   # Pronunciation 3 (for variant 2)
    (?:\s*\((?P<pren1a>[^\)]+)\)\s*)?               # parenthesized 1a
    (?:,?\s*(?P<part1a>(?:(?:{})\s*\.\s*)+))?       # part of speech for first definition (order varies)
    (?:\s*;\s+pl\.\s+(?P<plural>[\w-]+))?           # plural form or suffix, usually for irregulars
    (?:\s*\((?P<pren1b>[^\)]+)\)\s*)?               # parenthesized 1b
    (?:\.?\s*\[(?P<brack1>[^\]]+)\]\s*)?            # bracketed
    (?P<sepsp1>[\s.,]*?)                      # non-greedy space, punctuation(period, comma)
    (?:\s*(?P<part1b>(?:(?:{})\s*\.\s*)+))?   # part of speech for first definition (order varies)
    (?:Etym:\s*\[(?P<etym_1>[^\]]+)\]\s*)?    # etymology
    (?:\((?P<dtype1>[A-Z][\w\s&]+\.)\)\s*)?   # subject field abbreviations, e.g. (Arch., Bot. & Zool.)
    (?:\s*(?P<dftag1>Defn:|1\.|\(a\))\s+\.?\s*(?P<defn_1>[^.]+\.))?\s*   # Defn 1 tag and first sentence of definition.
    (?P<defn1a>[A-Z][^.]+\.)?\s*              # definition 1 sentence 2
    (?P<cetera>.*)?$                          # etc.
""".format(REP_PART, REP_PART), re.DOTALL|re.MULTILINE|re.VERBOSE)


'''

    (?:;)?\s*                                 # optional separator
    (?P<usage1>".*"[^\d]+)?\s*                # example 1
    (?P<defn_2>\d.\s[^\d]+)?                  # definition 2, ...
    (?:\s*(?P<part1b>(?:(?:{})\s*\.\s*)+))?   # part of speech for first definition (order varies)
    (?:\((?P<pren1c>[^\)]+)\)\s*)?            # parenthesized 1c
    (?:Etym:\s*\[(?P<etym_1>[^\]]+)\]\s*)?    # etymology


  Webster:
    (?:(?P<dftag1>Defn:|1\.)\s+\.?\s*(?P<defn_1>[^.]+\.))?\s+   # Defn 1 tag and first sentence of definition.


  Partial (backup, to be deleted)
    ^(?P<word_1>(?:[A-Z]+['-]?\ ?)+[A-Z]+['-]?|[A-Z]+['-]?|-[A-Z]+) # Primary WORD and whitespace
    (?:;\s+(?P<word_2>[A-Z'-]+))?                   # WORD 2 (variant spelling)
    (?:;\s+(?P<word_3>[A-Z'-]+))?\s+                # WORD 3 (variant spelling)
    (?P<pron_1>[A-Z](?:\w+['"*-]?\ ?)+\w+['"*-]?|[A-Z][^\s\(\[.,]+|[A-Z]\w+\s(?!Defn)\w+|-\w+) # Pron 1 (Capitalized)
    (?:,\s*(?P<pron_2>[A-Z][^\s\(\[,.]+))?          # Pronunciation 2 (for variant 2)
    (?:,\s*(?P<pron_3>[A-Z][^\s\(\[,.]+))?[.,]\s*   # Pronunciation 3 (for variant 2)
    (?P<pren1a>\([^\)]+\))?                         # parenthesized 1a
    (?:\s*(?P<part1a>(?:(?:{})\s*\.\s*)+))?         # part of speech for first definition (order varies)
    (?P<pren1b>\([^\)]+\))?                         # parenthesized 1b
    (?P<brack1>\[[^\]]+\])?                         # bracketed
    (?P<sepsp1>[\s.,]*?)                      # non-greedy space, punctuation(period, comma)
    (?:\s*(?P<part1b>(?:(?:{})\s*\.\s*)+))?   # part of speech for first definition (order varies)
    (?P<pren1c>\([^\)]+\))?                   # parenthesized 1c ?
    (?:Etym:\s*\[(?P<etym_1>[^\]]+)\]\s+)?    # etymology
    (?:\((?P<dtype1>[A-Z][\w\s&]+\.)\)\s+)?   # subject field abbreviations, e.g. (Arch., Bot. & Zool.)
    (?:\s+(?P<dftag1>Defn:|1\.)\s+\.?\s*(?P<defn_1>[^.]+\.))?\s*   # Defn 1 tag and first sentence of definition.
    (?P<defn1a>[A-Z][^.]+\.)?\s*              # definition 1 sentence 2
    (?:;)?\s*                                 # optional separator
    (?P<usage1>".*"[^\d]+)?\s*                # example 1
    (?P<defn_2>\d.\s[^\d]+)?                  # definition 2, ...
    (?P<cetera>.*)?$                          # etc.
'''

###############################################################################
def try_partial_match(entry, reason, verbose):
    '''test a variant of the webster regex'''
    if verbose > 2:
        print("\n++++++++++++++ Try partial match because:  %s:" % reason)
    match = REC_PARTIAL.match(entry)
    if match:
        return match
    if verbose > 1:
        print("======================================= Even partial match failed!")
    return None

def show_partial_match(partial, verbose):
    matgadd = defaultdict(str, partial.groupdict())
    if verbose > 2:
        put("\t",
            "word_1: (", matgadd["word_1"], ") \t",
            "word_2: (", matgadd["word_2"], ") \t",
            "word_3: (", matgadd["word_3"], ") \n\t",
            "pron_1: (", matgadd["pron_1"], ") \t",
            "pron_2: (", matgadd["pron_2"], ") \t",
            "pron_3: (", matgadd["pron_3"], ") \n\t",
            "pren1a: (", matgadd["pren1a"], ") \n\t",
            "part1a: (", matgadd["part1a"], ") \t",
            "plural: (", matgadd["plural"], ") \n\t",
            "pren1b: (", matgadd["pren1b"], ") \n\t",
            "brack1: (", matgadd["brack1"], ") \n\t",
            "sepsp1: (", matgadd["sepsp1"], ") \n\t",
            "part1b: (", matgadd["part1b"], ") \n\t",
            "pren1c: (", matgadd["pren1c"], ") \n\t",
            "etym_1: (", matgadd["etym_1"], ") \n\t",
            "dtype1: (", matgadd["dtype1"], ") \t",
            "dftag1: (", matgadd["dftag1"], ") \n\t",
            "defn_1: (", matgadd["defn_1"], ") \n\t",
            "defn1a: (", matgadd["defn1a"], ") \n\t",
            "cetera: (", matgadd["cetera"], ") \n\t",
            )
    return matgadd


###############################################################################
class WebsterEntry:
    '''Represents a parsed dictionary entry a la Webster's Unabridged'''
    def __init__(self, entry_dict):
        '''TODO: bifurcate on word_2 if present'''
        self.dict = entry_dict
        self.word_1 = entry_dict['word_1'].lower()
        word_2 = entry_dict['word_2']
        self.word_2 = word_2.lower() if word_2 else None
        word_3 = entry_dict['word_3']
        self.word_3 = word_3.lower() if word_3 else None
        self.pron_1 = entry_dict['pron_1']
        self.pron_2 = entry_dict['pron_2']
        self.pron_3 = entry_dict['pron_3']
        self.pren1a = entry_dict['pren1a']
        self.pren1b = entry_dict['pren1b']
        # self.pren1c = entry_dict['pren1c']    # TODO  remove
        self.brack1 = entry_dict['brack1']
        self.sepsp1 = entry_dict['sepsp1']
        part1 = entry_dict['part1a']
        self.part_1 = part1 if part1 else entry_dict['part1b']
        self.etym_1 = entry_dict['etym_1']
        self.dftag1 = entry_dict['dftag1']
        self.defn_1 = entry_dict['defn_1']
        self.defn1a = entry_dict['defn1a']
        self.usage1 = entry_dict['usage1']
        self.defn_2 = entry_dict['defn_2']
        self.cetera = entry_dict['cetera']

    def __str__(self):
        return('''
    word_1: {:<24}    word_2: {}    word_3: {}
    pron_1: {:<24}    pron_2: {}    pron_3: {}
    part_1: ({})
    brack1: ({})
    etym_1: ({})
    dftag1: ({})
    defn_1: ({})
    defn1a: ({})
    usage1: ({})
    defn_2: ({})
    cetera: ({})
    '''.format(self.word_1, self.word_2, self.word_3, self.pron_1, self.pron_2, self.pron_3,
               self.part_1, self.brack1, self.etym_1, self.dftag1, self.defn_1, self.defn1a, self.usage1,
               self.defn_2,
               self.cetera
              ))

    def variants(self):
        '''return list of variant spellings'''
        variants = [self.word_1]
        if self.word_2:
            variants.append(self.word_2)
            if self.word_3:
                variants.append(self.word_3)
        return variants

    def parts_of_speech(self):
        '''return all identified parts of speech abbreviations'''
        return self.part_1

def match_webster_entry(entry):
    '''return regex match on dictionary entry text; trying only one pattern for now'''
    return REC_WEBSTER.match(entry)

def parse_webster_entry(entry):
    '''Return a dict representing a parsed dictionary entry.
    For now we just return the dict from a match's named groups.'''
    match = match_webster_entry(entry)
    if match:
        return match.groupdict()
    return None

def common_and_max_len(str_a, str_b):
    '''return index of first difference between two strings, or in other words,
    the length of their common leading substrings, and the maximum of their
    lengths.  May be applied to other subscriptables besides strings.'''
    maxlen = max(len(str_a), len(str_b))
    for idx in range(maxlen):
        try:
            if str_a[idx] != str_b[idx]:
                return idx, maxlen
        except IndexError:
            break
    return idx + 1, maxlen

def index_diff(sub_a, sub_b):
    '''
    Return index of first difference between two strings or other
    subscriptable objects, or in other words, the length of their common prefixes.
    '''
    for idx, tup in enumerate(zip(sub_a, sub_b)):
        if tup[0] != tup[1]:
            return idx
    return idx + 1 if idx else 0


def parse_webster_file(path, opts, verbose=1):
    '''parse Webster-like dictionary text file with diagnostics.'''
    metrics = defaultdict(int)
    partial = REC_PARTIAL.pattern
    webster = REC_WEBSTER.pattern
    comlen, totlen = common_and_max_len(partial, webster)
    is_partial_different = comlen < totlen
    if verbose > 1:
        if is_partial_different:
            print("Partial pattern matches Webster pattern up to:  %d/%d" % (comlen, totlen))
            print("Webster____%s____" % webster[comlen-24:comlen+24])
            print("Partial____%s____" % partial[comlen-24:comlen+24])
        else:
            print("Partial == Webster pattern:", totlen)
    for idx, entry_text in enumerate(para_ns_iter_lex_file(path, REC_UPPER_WORD, sep_lines=1, charset=opts.charset)):
        if idx >= opts.start_index:
            metrics['tried'] += 1
            is_undefined = True
            entry_dict = parse_webster_entry(entry_text)
            if entry_dict:
                metrics['parsed'] += 1
                if entry_dict['defn_1']:
                    metrics['defined'] += 1
                    is_undefined = False
                entry_base = WebsterEntry(entry_dict)
                if verbose > 5 or verbose > 2 and is_undefined:
                    print("\nPARAGRAPH {:5}\n({})".format(idx, entry_text))
                if verbose > 4:
                    print("WebsterEntry:", entry_base)
            else:
                metrics['unparsed'] += 1
                if verbose > 2:
                    print("\nPARAGRAPH {:5}\n({})".format(idx, entry_text))
                if verbose > 1:
                    print(" {:<20} >>>>NO MATCH<<<< {:>6}".format(first_token(entry_text), idx))
            if is_partial_different:
                if not entry_dict:
                    reason = "Main Match Failed"
                elif is_undefined:
                    reason = "Definition Not Found"
                elif verbose > 6:
                    reason = "verbose > 6"
                elif opts.both:
                    reason = "Parse Both Ways To Compare"
                else:
                    reason = None
                if reason:
                    partial = try_partial_match(entry_text, reason, verbose)
                    if partial:
                        metrics['parted'] += 1
                        part_dict = show_partial_match(partial, verbose)
                        if part_dict['defn_1']:
                            metrics['partdef'] += 1
                    else:
                        metrics['unparted'] += 1
        if opts.stop_index > 0 and idx >= opts.stop_index:
            break
    print_metrics(metrics)

def percent(count, total):
    '''count/total as a percentage, or NAN if total <= 0'''
    return 100.0 * count / total if total > 0 else float('nan')

def print_metrics(metrics):
    '''pretty print metrics dict'''
    print("For %d tried, defined/parsed: Full: %d/%d, Part: %d/%d ==> %.1f%% v. %.1f%% & Max Parsed %.1f%%.  " % (
        metrics['tried'],
        metrics['defined'], metrics['parsed'],
        metrics['partdef'], metrics['parted'],
        percent(metrics['defined'], metrics['parsed']),
        percent(metrics['partdef'], metrics['parted']),
        percent(max(metrics['parsed'], metrics['parted']), metrics['tried'])),
        end='')
    print("Failures:   Full %d & %d   Part %d & %d" % (
        metrics['tried'] - metrics['defined'], metrics['unparsed'],
        metrics['tried'] - metrics['partdef'], metrics['unparted']))

CONST_MAX_WORDS = 5
DEFAULT_NUMBER = 10
CONST_START_INDEX = 1
CONST_STOP_INDEX = 10
DEFAULT_START_INDEX = 0
DEFAULT_STOP_INDEX = 0

def main():
    '''Driver to iterate over the paragraphs in a text file.'''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('text_file', type=str, nargs='?', default='corpus.txt',
                        help='text file containing quoted dialogue')
    parser.add_argument('-both', action='store_true',
                        help='Try both match-parsers.')
    parser.add_argument('-charset', dest='charset', type=str, default='iso-8859-1',
                        help='charset encoding of input text')
    parser.add_argument('-function', type=int, nargs='?', const=1, default=0,
                        help='paragraph printing function: 0=all (default: 0)')
    parser.add_argument('-number', type=int, nargs='?', const=CONST_MAX_WORDS,
                        default=DEFAULT_NUMBER,
                        help='max number of entries to parse (defaults: %d/%d)' % (
                            CONST_MAX_WORDS, DEFAULT_NUMBER))
    parser.add_argument('-start_index', '-beg', type=int, nargs='?',
                        const=CONST_START_INDEX, default=DEFAULT_START_INDEX,
                        help='start_index (defaults: %d/%d)' % (CONST_START_INDEX, DEFAULT_START_INDEX))
    parser.add_argument('-stop_index', '-end', type=int, nargs='?',
                        const=CONST_STOP_INDEX, default=DEFAULT_STOP_INDEX,
                        help='stop_index (defaults: %d/%d)' % (CONST_STOP_INDEX, DEFAULT_STOP_INDEX))
    parser.add_argument('-webster', action='store_true',
                        help='parse a dictionary in the format of Websters Unabridged.')
    parser.add_argument('-words', dest='max_words', type=int, nargs='?', const=CONST_MAX_WORDS, default=0,
                        help='maximum words per paragraph: print only the first M words,\
                        or all if M < 1 (default: 0)')
    parser.add_argument('-verbose', type=int, nargs='?', const=1, default=1,
                        help='verbosity of output (default: 1)')
    args = parser.parse_args()
    verbose = args.verbose

    if args.webster:
        parse_webster_file(args.text_file, args, verbose)
        exit(0)

    if args.function == 0:
        print_paragraphs(args.text_file)
    elif args.function == 1:
        print_paragraphs_trunc(args.text_file, args.max_words)
    elif args.function == 2:
        print_paragraphs_split_join_str(args.text_file, args.max_words)
    elif args.function == 3:
        print_paragraphs_split_join_rgx(args.text_file, args.max_words)
    elif args.function == 4:
        print_paragraphs_nth_substr(args.text_file, args.max_words)
    elif args.function == 5:
        print_paragraphs_nth_regex(args.text_file, args.max_words)
    else:
        print("\n\t LEAKY VERSION: \n")
        print_paragraphs_leaky(args.text_file)

if __name__ == '__main__':
    main()
