#!/usr/bin/env python3
# Sprax Lines       2016.09.26      Written for Python 3.5
'''Output some dates.'''

import argparse
import datetime
import re
import sys
import time

import paragraphs
from utf_print import utf_print

# DAY_CODES = ['Mnd', 'Tsd', 'Wnd', 'Thd', 'Frd', 'Std', 'Snd']

def print_dates(out_format, start_date, offset_days, num_days, per_day, verbose):
    '''Output num_days consecutive formatted dates from start_date'''
    date = start_date
    date += datetime.timedelta(days=offset_days)
    # for _ in itertools.repeat(None, num_days):
    for _ in range(num_days):
        tstm = date.timetuple()
        if verbose > 2:
            print(tstm)
        dstr = time.strftime(out_format, tstm)
        if tstm.tm_wday < 5:
            locs = 'Home/CIC'
        elif tstm.tm_wday == 5:
            locs = 'Home/NH'
        else:
            locs = 'Home/MIT'
        # code = DAY_CODES[tstm.tm_wday]
        # print(tstm)
        # print("%s ==> %s %s\t%s" % (date, dstr, code, locs))
        if per_day > 1:
            print("%s AM \t%s" % (dstr, locs))
            print("%s PM \t%s" % (dstr, 'Home'))
        else:
            print("%s\t%s" % (dstr, locs))
        date += datetime.timedelta(days=1)

def try_parse_date(text, input_formats):
    '''Try to extract a date by matching the input date formats.'''
    date = None
    for date_format in input_formats:
        try:
            date = datetime.datetime.strptime(text, date_format)
            return date
        except ValueError:
            pass
    return None

def reformat_date(text, out_format, input_formats, verbose):
    '''If text parses as a date of one of the specified formats, return that date.
    Otherwise, return text as-is.'''
    date = try_parse_date(text, input_formats)
    if date:
        tstm = date.timetuple()
        if verbose > 2:
            print(date, '=>', tstm)
        return time.strftime(out_format, tstm)
    else:
        return text

def replace_first_date(text, out_format, input_formats, verbose):
    '''Replace any recognized date at the start of text with one of the specified format.'''
    date_first_pat = r"^\s*(\d\d\d\d\.\d\d\.\d\d)'(.*?)[,.!?]'(\s*|$)"
    rgx_date = re.compile(date_first_pat)
    matched = re.match(rgx_date, text)
    if matched:
        raw_date, body = matched.groups()
        ref_date = reformat_date(raw_date, out_format, input_formats, verbose)
        if verbose > 3:
            print(ref_date)
        return "\t".join(ref_date, body)
    return text

def replace_dates(texts, out_format, input_formats, verbose):
    '''Replace any recognized date at the start of text with one of the specified format.'''
    texts_out = []
    for text in texts:
        text_out = replace_first_date(text, out_format, input_formats, verbose)
        if verbose > 3:
            print(text_out)
        texts_out.append(text_out)
    return texts_out



def reformat_paragraphs(path, verbose, charset='utf8'):
    '''Parses paragraphs into leading date, first sentence, and body.
    Reformats the date, if present.'''
    with open(path, 'r', encoding=charset) as text:
        for idx, para in enumerate(paragraphs.paragraph_iter(text)):
            if verbose > 2:
                print("    Paragraph {}:".format(idx))
            # para = para.replace('’', "'")
            yield extract_date_head_body(para, verbose)

# rgx_qt = re.compile(r"(?:^\s*|said\s+|says\s+|\t\s*|[,:-]\s+)['\"](.*?)([,.!?])['\"](?:\s+|$)")

# @staticmethod
# def tag_regex(tagsymbols):
    # pattern = r'(?u)\s([{tags}][-+*#&/\w]+)'.format(tags=tagsymbols)
    # return re.compile( pattern, re.UNICODE )

def dated_entry_regex():
    date_grp_str = r'\s*(\d\d\d\d.\d\d.\d\d)\s+'
    wday_grp_str = r'(?:(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+)?'
    place_grp_str = r'\s*(\d\d\d\d.\d\d.\d\d)'
    pattern = r"{}{}(.*)".format(date_grp_str, wday_grp_str)
    return re.compile( pattern, re.UNICODE )

def extract_date_head_body(paragraph, verbose):
    '''return date string, head, and body frmo paragraph'''
    if not paragraph:
        print("WARNING: paragraph is empty!")
        return ()
    if verbose > 2:
        utf_print("edhb: ", paragraph)
    rem = re.match(dated_entry_regex(), paragraph)
    if rem:
        return rem.groups()
    else:
        return ()

def main():
    '''get args and call print_dates'''
    default_format = '%Y.%m.%d %a'
    default_num_days = 7
    default_jrnl_input = "djs.txt"
    default_start_date = start_date = datetime.datetime.now()
    parser = argparse.ArgumentParser(
        # usage='%(prog)s [options]',
        description="Read/write journal-entry style dates"
        )
    parser.add_argument('offset_days', type=int, nargs='?', default=0,
                        help='offset from start date (default: today) to first output date')
    parser.add_argument('num_days', type=int, nargs='?', default=default_num_days,
                        help="number of days' dates to output (default: {})"
                        .format(default_num_days))
    parser.add_argument('per_day', type=int, nargs='?', default=1,
                        help='number of entries per day (default: 1)')
    parser.add_argument('-jrnl_input', metavar='FILE', type=str,
                        help='convert dated-entry text file to jrnl format (default: {})'
                        .format(default_jrnl_input))
    parser.add_argument('-out_format', metavar='FORMAT', type=str,
                        help='output date format (default: {})'
                        .format(default_format.replace('%', '%%')))
    parser.add_argument('-start_date', metavar='DATE', type=str,
                        help='start date (default: today)')
    parser.add_argument('-verbose', type=int, nargs='?', const=1, default=1,
                        help='verbosity of output (default: 1)')
    args = parser.parse_args()

    out_format = args.out_format if args.out_format else default_format

    if args.start_date:
        try:
            start_date = datetime.datetime.strptime(args.start_date, out_format)
        except ValueError:
            print("WARNING: Failed to parse start date: {}; using default: {}"
                  .format(args.start_date, start_date))

    if args.jrnl_input:
        print("convert diary to jrnl format: coming soon...")
        refs = reformat_paragraphs(args.jrnl_input, args.verbose)
        for ref in refs:
            for part in ref:
                utf_print(part)
            print()
            # utf_print('ref: ', ref[0] if len(ref) > 0 else ref)
    else:
        print_dates(out_format, start_date, args.offset_days, args.num_days
                    , args.per_day, args.verbose)

if __name__ == '__main__':
    main()

'''
>>> dates = 'date'
>>> first = r'[\w][^.!?]+[.!?]'
>>> bodys = '.*'
>>> rgx = re.compile("({})\s+({})\s+({})".format(dates, first, bodys)
... )
>>>
>>>
>>>
>>> rgx
re.compile('(date)\\s+([\\w][^.!?]+[.!?])\\s+(.*)')
>>> sent = 'date 8*^)_+(*+(@(#_+&_+@#$%^&*()$#@%'
>>> m = rgx.match(sent)
>>> m
>>> m = re.match(rgx, sent)

>>> dates = 'date'
>>> first = r'[\w][^.!?]+[.!?]'
>>> bodys = '.*'
>>> rgx = re.compile("({})\s+({})\s+({})".format(dates, first, bodys)
>>>
>>> rgx
re.compile('(date)\\s+([\\w][^.!?]+[.!?])\\s+(.*)')
>>> sent = 'date 8*^)_+(*+(@(#_+&_+@#$%^&*()$#@%'
>>> m = rgx.match(sent)
>>> m
>>> m = re.match(rgx, sent)
>>>
'''

