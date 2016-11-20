#!/usr/bin/env python3
# Sprax Lines       2016.09.26      Written for Python 3.5
'''Parse a debate transcript into speaker turns:
N > 1 contestants each have approximately the same number T of turns,
M >= 0 moderators collectively have somewhere between T and N*T turns,
and each turn is an array of one or more paragraphs, each of which
divides into one or more sentences.
'''

import argparse
import datetime
import re

import paragraphs
from utf_print import utf_print

def main():
    '''get args and call ...'''
    default_debate_text = "djs.txt"
    # default_start_date = start_date = datetime.datetime.now()
    parser = argparse.ArgumentParser(
        # usage='%(prog)s [options]',
        description="Read/write journal-entry style dates"
        )
    parser.add_argument('debate_text', metavar='TRANSCRIPT', type=str,
                        help='convert speaker-labeled text file to paragraphs (default: {})'
                        .format(default_debate_text))
    parser.add_argument('-max_words', type=int, nargs='?', const=1, default=7,
                        help='maximum words per paragraph: print only the first M words,\
                        or all if M < 1 (default: 0)')
    parser.add_argument('-num_turns', type=int, nargs='?', const=1, default=15,
                        help='number of turns to show, or 0 for all (the default)')
    parser.add_argument('-verbose', type=int, nargs='?', const=1, default=1,
                        help='verbosity of output (default: 1)')
    args = parser.parse_args()

    debate = Debate(args.debate_text, args.verbose)
    for turn in debate.all_turns[:args.num_turns]:
        print(turn.speaker)
        for para in turn.text:
            paragraphs.print_paragraph_regex_count(para, args.max_words)
        print()
    # now summarize it...

class DebateTurn:
    '''one speaker turn in a debate'''
    def __init__(self, speaker, date, text):
        self.speaker = speaker
        self.date = date
        self.text = [text]

class Debate:
    '''Initialize debate as a sequence of turns by moderators and contestants.'''
    def __init__(self, transcript, verbose):
        self.speakers = set()
        self.moderators = set()
        self.debaters = set()
        self.turn_count = 0
        self.all_turns = []
        self.speaker_turns = {}
        self.verbose = verbose
        self.parse_transcript(transcript)

    def parse_transcript(self, transcript_file):
        '''Populates Debate data: array of all speaker turns as one sequence,
        and dictionary mapping each speaker to an array of turn indices.'''
        verbose = 1
        turn = DebateTurn('[debate start]', datetime.datetime.now(), '')
        prev_speaker = ''
        self.all_turns.append(turn)
        for para in reformat_paragraphs(transcript_file):
            if is_comment(para):
                continue
            refd = None
            (speaker, date, body) = extract_speaker_date_body(para, verbose)
            if date:
                refd = date
                print("\t  date:\t", refd)
            if speaker and speaker != prev_speaker:
                prev_speaker = speaker
                self.add_speaker(speaker)
                turn = DebateTurn(speaker, refd, body)
                self.all_turns.append(turn)
                self.speaker_turns[speaker].append(turn)
            elif body:
                body = body.replace('’', "'")
                turn.text.append(body)
            elif self.verbose > 2:
                print("______parse_paragraph: discarding:\n", para)

    def add_speaker(self, speaker):
        if speaker not in self.speakers:
            self.speakers.add(speaker)
            self.speaker_turns[speaker] = []
            print("<==== new speaker: ", speaker, '====>')

    def add_moderator(self, name):
        if name in self.debaters:
            raise ValueError('moderator error: ' + name + ' already in debators')
        self.moderators.add(name)
        self.add_speaker(name)

    def add_debater(self, name):
        if name in self.moderators:
            raise ValueError('debater error: ' + name + ' already in moderators')
        self.debaters.add(name)
        self.add_speaker(name)

    def get_turns(self, speaker_name):
        return self.speaker_turns[speaker_name]

    def print_first_per_turn(self, max_words):
        '''Print beginning of turns, up to max words.'''
        for turn in self.all_turns:
            print(turn.speaker)
            for para in turn.text:
                paragraphs.print_paragraph_regex_count(para, max_words)
            print()

def reformat_paragraphs(path, charset='utf8'):
    '''Just get the paragraphs.'''
    with open(path, 'r', encoding=charset) as text:
        for para in paragraphs.paragraph_iter(text):
            yield para

def is_comment(string):
    '''comments start with # or // or /* ... ?'''
    return string[0] == '#'


def extract_speaker_date_body(paragraph, verbose):
    '''extract (date, head, body) from paragraph, where date and body may be None'''
    rem = re.match(speaker_dated_entry_regex(), paragraph)
    if rem:
        if verbose > 2:
            for part in rem.groups():
                utf_print("\t", part)
            print()
        return rem.groups()
    else:
        return (None, None, paragraph)

# rgx_qt = re.compile(r"(?:^\s*|said\s+|says\s+|\t\s*|[,:-]\s+)['\"](.*?)([,.!?])['\"](?:\s+|$)")
# @staticmethod
# def tag_regex(tagsymbols):
    # pattern = r'(?u)\s([{tags}][-+*#&/\w]+)'.format(tags=tagsymbols)
    # return re.compile( pattern, re.UNICODE )

# @staticmethod
def speaker_dated_entry_regex():
    '''return compiled regex pattern'''
    spkr_grp = r'(?:\s*([A-Z]+):(?:\s*))?'
    date_grp = r'(?:\s*(\d\d\d\d.\d\d.\d\d|\d\d.\d\d.\d\d)[-\s])?'
    body_grp = r'(?:\s*)?(\S.*)?'
    pattern = r"{}{}{}".format(spkr_grp, date_grp, body_grp)
    return re.compile(pattern, re.UNICODE)


if __name__ == '__main__':
    main()
