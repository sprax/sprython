#!/usr/bin/env python3
'''nltk_book.py'''

from collections import Counter
import nltk

def lexical_diversity(text):
    '''ratio of word count to unique word count'''
    return len(text) / len(set(text))

def freq(text, word):
    '''frequency of a single word'''
    return text.count(word) / len(text)

def frac(text, word_set):
    '''fraction of text comprised of words in word_set'''
    total = sum([text.count(word) for word in word_set])
    return total / len(text)

def counter(text):
    '''Counter of words'''
    return Counter(text)

def bigrams_counter(text, min_len):
    '''Counter of bigrams'''
    counter = Counter()
    for big in nltk.bigrams(text):
        if len(big[0]) > min_len and len(big[1]) > min_len:
            counter.update([big])
    return counter

def trigrams_counter(text, min_len, min_sum_len):
    '''Counter of trigrams'''
    counter = Counter()
    for trig in nltk.trigrams(text):
        len0 = len(trig[0])
        if len0 < min_len:
            continue
        len1 = len(trig[0])
        if len1 < min_len:
            continue
        len2 = len(trig[2])
        if len2 < min_len:
            continue
        if len0 + len1 + len2 < min_sum_len:
            continue
        counter.update([trig])
    return counter

def generate_model(cfdist, word, length=15):
    words = [word]
    for _ in range(length):
        word = cfdist[word].max()
        if word not in words:
            words.append(word)
    print(' '.join(words))

def test_nltk_book(text):
    '''test module methods'''
    trig_counter = trigrams_counter(text)

if __name__ == '__main__':
    test_nltk_book()
