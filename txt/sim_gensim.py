#!/usr/bin/env python3
'''
word2vec similarity
TODO: understand accuracy, and some others in:
    ['_load_specials', '_save_specials', '_smart_save', 'accuracy', 'doesnt_match',
    'evaluate_word_pairs', 'get_embedding_layer', 'index2word', 'init_sims', 'load',
    'load_word2vec_format', 'log_accuracy', 'log_evaluate_word_pairs', 'most_similar',
    'most_similar_cosmul', 'n_similarity', 'save', 'save_word2vec_format',
    'similar_by_vector', 'similar_by_word', 'similarity', 'syn0', 'syn0norm',
    'vector_size', 'vocab', 'wmdistance', 'word_vec', 'wv']
'''
from __future__ import division
# import nltk
# import scipy
import inspect
import string
import re
import time
import gensim
# from gensim.models import Word2Vec
# from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from scipy.spatial.distance import cosine

def default_word2vec_model(verbose=True):
    '''Load pre-made word2vec model'''
    # TODO: Use _save_specials and _load_specials?
    beg = time.time()
    model = gensim.models.KeyedVectors.load_word2vec_format(
        'Text/GoogleNews-vectors-negative300.bin', binary=True)
    if verbose:
        print("Seconds to load_word2vec_format:", time.time() - beg)
        # Seconds to load_word2vec_format: 44.98383688926697
    return model

def model_vocab(model, verbose=True):
    '''Initialize vocab as the set of keys from a word2vec model'''
    beg = time.time()
    vocab = set([key for key in model.vocab.keys()])
    if verbose:
        print("Seconds to initialize vocab model:", time.time() - beg)
        # Seconds to initialize vocab model: 1.3567819595336914
    return vocab

def default_stop_words():
    '''get the default stop words'''
    # TODO: exclude who, what, when, where, why, etc.
    return stopwords.words('english')

def vocab_words(vocab, tokens):
    '''filtered words: returns the list of in-vocabulary words from a list of tokens'''
    return [tok for tok in tokens if tok in vocab]

def word_tokens(vocab, text):
    '''return list of word tokens from string'''
    # TODO: use tokenizer from emo project that saves contractions.
    # TODO: Replace "didn't" with "did not", etc.?  What does the model do?
    busted = re.sub(r'[\d%s]' % string.punctuation, ' ', text)
    tokens = word_tokenize(busted)
    return vocab_words(vocab, tokens)

def similarity(vec_a, vec_b):
    '''similarity as cosine (dot product)'''
    return cosine(vec_a, vec_b)

def distance(vec_a, vec_b):
    '''distance as 1.0 - dot_product'''
    return 1.0 - similarity(vec_a, vec_b)

def sum_sentence_similarity(model, vocab, sent_1, sent_2):
    '''crude sentence-content similarity based on summing word vectors'''
    vsent_1 = sum([model[tok] for tok in word_tokens(vocab, sent_1)])
    vsent_2 = sum([model[tok] for tok in word_tokens(vocab, sent_2)])
    return similarity(vsent_1, vsent_2)

def sum_tokens(model, tokens, verbose=False):
    '''Vector sum of in-vocabulary word vectors from tokens.'''
    v_sum = None
    for token in tokens:
        try:
            v_tok = model[token]
            v_sum = v_tok if v_sum is None else v_sum + v_tok
        except KeyError as ex:
            if verbose:
                print("KeyError in", inspect.currentframe().f_code.co_name, ':', ex)
    return v_sum

def sum_tokens_similarity(model, tokens_1, tokens_2, verbose=False):
    '''
    Crude token-list content similarity based on summing word vectors.
    Only in-vocabulary tokens contribute; others are ignored.
    '''
    v_sum_1 = sum_tokens(model, tokens_1, verbose)
    v_sum_2 = sum_tokens(model, tokens_2, verbose)
    return cosine(v_sum_1, v_sum_2)

def compare_token_lists(model, tokens_1, tokens_2, verbose=True):
    '''Show crude token-list content similarity based on summing word vectors.'''
    sim = sum_tokens_similarity(model, tokens_1, tokens_2, verbose)
    dif = 1.0 - sim
    st1 = ' '.join(tokens_1)
    st2 = ' '.join(tokens_2)
    if verbose:
        print("Comparing (%s) & (%s) %s sim %.5f  dif %.5f" % (st1, st2, " "*(24 - len(st1 + st2)), sim, dif))
    return sim

#################################### TESTS ####################################

def test_word_similarity(model, aa='king', bb='queen', cc='man', dd='woman'):
    '''show similarity on a tetrad of (analogous) words'''
    print("test_word_similarity:", test_word_similarity.__doc__)
    sim_aa = model.similarity(aa, aa)
    sim_bb = model.similarity(bb, bb)
    absdif = abs(sim_aa - sim_bb)
    print("self similarities of %s and %s to themselves:\t%f and %f, dif %f" %
          (aa, bb, sim_aa, sim_bb, absdif))
    sim_ab = model.similarity(aa, bb)
    sim_ba = model.similarity(bb, aa)
    absdif = abs(sim_ab - sim_ba)
    print("symm similarities of %s to %s and %s to %s:\t%f and %f, dif %f" %
          (aa, bb, bb, aa, sim_ab, sim_ba, absdif))
    sim_ab = model.similarity(aa, bb)
    sim_cd = model.similarity(cc, dd)
    absdif = abs(sim_ab - sim_cd)
    print("opposite sims a:b:c:d %s to %s and %s to %s:\t%f and %f, dif %f" %
          (aa, bb, cc, dd, sim_ab, sim_cd, absdif))
    sim_ac = model.similarity(aa, cc)
    sim_bd = model.similarity(bb, dd)
    absdif = abs(sim_ac - sim_bd)
    print("analogous sims a:c:b:d %s to %s and %s to %s:\t%f and %f, dif %f" %
          (aa, cc, bb, dd, sim_ac, sim_bd, absdif))

def test_word_differences(model, aa='king', bb='queen', cc='man', dd='woman'):
    '''show differences on a tetrad of (analogous) words'''
    vec_aa = model[aa]
    vec_bb = model[bb]
    vec_cc = model[cc]
    vec_dd = model[dd]

    dif_ab = vec_aa - vec_bb
    dif_cd = vec_cc - vec_dd
    sim_xx = cosine(dif_ab, dif_cd)
    print("similarity of vec(%s) - vec(%s) to vec(%s) - vec(%s): %f" % (aa, bb, cc, dd, sim_xx))

    dif_ac = vec_aa - vec_cc
    dif_bd = vec_bb - vec_dd
    sim_yy = cosine(dif_ac, dif_bd)
    print("similarity of vec(%s) - vec(%s) to vec(%s) - vec(%s): %f" % (aa, cc, bb, dd, sim_yy))

def test_word_analogies(model, aa='king', bb='queen', cc='man', dd='woman'):
    '''show arithmetic combos on a tetrad of (analogous) words'''
    vec_aa = model[aa]
    vec_bb = model[bb]
    vec_cc = model[cc]
    vec_dd = model[dd]
    vec_acd = vec_aa - vec_cc + vec_dd
    vec_bdc = vec_bb - vec_dd + vec_cc
    sim_acdb = cosine(vec_acd, vec_bb)
    print("similarity of vec(%s) - vec(%s) + vec(%s) to vec(%s): %f" % (aa, cc, dd, bb, sim_acdb))
    sim_bdca = cosine(vec_bdc, vec_aa)
    print("similarity of vec(%s) - vec(%s) + vec(%s) to vec(%s): %f" % (bb, dd, cc, aa, sim_bdca))

def test_sentence_distance(model, vocab, sent_1="This is a sentence.",
                           sent_2="This, IS, some, OTHER, Sentence!"):
    '''show simple sub-based sentence distance'''
    toks_1 = word_tokens(vocab, sent_1)
    toks_2 = word_tokens(vocab, sent_2)
    print("word_tokens({}) == {}".format(sent_1, toks_1))
    print("word_tokens({}) == {}".format(sent_2, toks_2))
    dist12 = sum_tokens_distance(model, vocab, sent_1, sent_2)
    print("sum_tokens_distance => ", dist12)

def test_contractions(model, verbose=True):
    t_do = ["do"]
    t_does = ["does"]
    t_did = ["did"]
    t_not = ["not"]
    t_do_not = t_do + t_not
    t_does_not = t_does + t_not
    t_did_not = t_did + t_not
    t_dont = ["don't"]
    t_doesnt = ["doesn't"]
    t_didnt = ["didn't"]
    compare_token_lists(model, t_do, t_does, verbose=True)
    compare_token_lists(model, t_do, t_did, verbose=True)
    compare_token_lists(model, t_do, t_not, verbose=True)

    compare_token_lists(model, t_do_not, t_not, verbose=True)
    compare_token_lists(model, t_do_not, t_does_not, verbose=True)
    compare_token_lists(model, t_do_not, t_did_not, verbose=True)

    compare_token_lists(model, t_do_not, t_dont, verbose=True)
    compare_token_lists(model, t_do_not, t_doesnt, verbose=True)
    compare_token_lists(model, t_do_not, t_didnt, verbose=True)

    compare_token_lists(model, t_does_not, t_dont, verbose=True)
    compare_token_lists(model, t_does_not, t_doesnt, verbose=True)
    compare_token_lists(model, t_does_not, t_didnt, verbose=True)

    compare_token_lists(model, t_did_not, t_dont, verbose=True)
    compare_token_lists(model, t_did_not, t_doesnt, verbose=True)
    compare_token_lists(model, t_did_not, t_didnt, verbose=True)

    compare_token_lists(model, t_dont, t_doesnt, verbose=True)
    compare_token_lists(model, t_dont, t_didnt, verbose=True)
    compare_token_lists(model, t_doesnt, t_didnt, verbose=True)

def smoke_test(model, vocab):
    '''sanity checking'''
    test_word_similarity(model)
    test_word_differences(model)
    test_word_analogies(model)
    test_sentence_distance(model, vocab)
    test_contractions(model, verbose=True)
