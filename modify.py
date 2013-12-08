# encoding: utf-8

import sys, os, shutil, time, argparse, datetime
import collections
import math
import numpy
import random
import re
import readline
import nltk

import classify as clf


from nltk.corpus import cmudict
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn import svm
from sklearn import metrics
from pattern.en import pluralize, conjugate, comparative, superlative

cd = cmudict.dict()
lmtzr = WordNetLemmatizer()
NUM_SENTENCES = 3
RHYMES = ["IH1", "AE1", "UW1", "EY2", "EH1", "UW2", "OW1", "IH2", "EY1", "ER1", "IY1", "AY1", "AH1", "AY2", "AW2", "AO1", "AW1", "AA1", "OW2", "EH2", "UH1", "OY2", "UH2", "ER2", "OY1", "AH2", "AE2", "IY2", "AO2"], "AA2"
DEBUG = False
# get a tuple of (doc_name, list_of_words, label) from a given file
def getWordsFromFile(filePath, fileName):
  f = open(os.path.join(filePath, fileName), 'r')
  # assuming the first line is the doc file
  # the second line is the body of text
  docName = f.readline()
  docBody = f.readline()
  sentences_raw = docBody.split('.')
  sentences = []

  # elminate empty and null values from string to prevent weird sentences
  # such as "  .   . . ."
  for s in sentences_raw:
    if s != None and s.strip() != '':
      sentences.append(s)

  if len(sentences) < (NUM_SENTENCES + 2):
    return None

  # start = random.randint(0, len(sentences) - 4)
  # deterministic version
  start = min(len(sentences) - 1 - NUM_SENTENCES, (len(sentences) - 1 - NUM_SENTENCES)/2)

  f.close()
  split = '.'
  docBody = split.join(sentences[start:start + NUM_SENTENCES]) + '.'
  docBody = docBody.replace("’","'")
  # tokens = []
  # for s in sentences[start:start + NUM_SENTENCES]:
  #   tokens += nltk.word_tokenize(s+" . ")

  # print tokens
  # print "\n"

  return (docName, nltk.pos_tag(re.findall(r"[\w']+|[.,!?;]", docBody)))

def convertToMostFrequentRhyme(words):
  pron = get_pronounce_list(words)

def attach_similar_words(words_w_tags):
  words_w_tags_and_similars = []
  for (word, tag) in words_w_tags:
    similar_words = []
    capitalized = word[0].isupper()
    try:
      if tag.startswith("NN"):
        word_l = lmtzr.lemmatize(word.lower())
        s_set = wn.synset(word_l+'.n.01')
        for s in s_set.hypernyms():
          w = s.name.split(".")[0].replace("_"," ")
          if tag[-1] == "S":
            w = pluralize(w)
          similar_words.append(w.capitalize() if capitalized else w)
        for l in s_set.lemmas:
          w = l.name.replace("_"," ")
          if tag[-1] == "S":
            w = pluralize(w)
          similar_words.append(w.capitalize() if capitalized else w)

      elif tag.startswith("VB"):
        word_l = lmtzr.lemmatize(word.lower(),"v")
        if word_l == "be": # handle special case "was"
          similar_words.append(word)
          words_w_tags_and_similars.append((word,tag,similar_words))
          continue
        s_set = wn.synset(word_l+'.v.01')
        for s in s_set.hypernyms():
          w = s.name.split(".")[0].replace("_"," ")
          if tag[-1] == "D":
            w = conjugate(w,"p")
          elif tag[-1] == "G":
            w = conjugate(w,"part")
          elif tag[-1] == "N":
            w = conjugate(w,"ppart")
          elif tag[-1] == "P":
            w = conjugate(w,"1sg")
          elif tag[-1] == "Z":
            w = conjugate(w,"3sg")
          similar_words.append(w.capitalize() if capitalized else w)
        for l in s_set.lemmas:
          w = l.name.replace("_"," ")
          if tag[-1] == "D":
            w = conjugate(w,"p")
          elif tag[-1] == "G":
            w = conjugate(w,"part")
          elif tag[-1] == "N":
            w = conjugate(w,"ppart")
          elif tag[-1] == "P":
            w = conjugate(w,"1sg")
          elif tag[-1] == "Z":
            w = conjugate(w,"3sg")
          similar_words.append(w.capitalize() if capitalized else w)

      elif tag.startswith("JJ"):
        word_l = lmtzr.lemmatize(word.lower(),"a")
        s_set = wn.synset(word_l+'.a.01')
        for s in s_set.hypernyms():
          w = s.name.split(".")[0].replace("_"," ")
          if tag[-1] == "R" and word != 'more':
            w = comparative(w)
          elif tag[-1] == "S" and word != 'most':
            w = superlative(w)
          similar_words.append(w.capitalize() if capitalized else w)
        for l in s_set.lemmas:
          w = l.name.replace("_"," ")
          if tag[-1] == "R":
            w = comparative(w)
          elif tag[-1] == "S":
            w = superlative(w)
          similar_words.append(w.capitalize() if capitalized else w)
    except:
      words_w_tags_and_similars.append((word,tag,similar_words))
      continue
    # print ( word, ": ", similar_words )
    # print "\n"
    words_w_tags_and_similars.append((word,tag,similar_words))
  return words_w_tags_and_similars

def rtn_modified_sentence(words_w_tags_and_similars):
  l = []
  for (word,tag,similar_words) in words_w_tags_and_similars:
    if len(similar_words) != 0:
      l.append(similar_words[int(random.random() * len(similar_words))])
    else:
      l.append(word)
  return l

def get_pronounce_list_for_words(words):
  pron = []
  for w in words:
    w = w.lower()
    if w in cd:
      pron.append(cd[w][0]) # pick the first pronounciation
  return pron

def get_rhym_distribution(pron):
  count = collections.Counter()
  for p in pron:
    for i in range(len(p)-1, -1, -1):
      bit = p[i]
      if (bit[-1] == '1' or bit[-1] == '2' or bit[-1] == '0') and (bit != 'AH0'):
        count[(bit, len(p)-1-i)] += 1.0
        break
  return count
  # arr = [(count[pair], pair) for pair in count]
  # arr = sorted(arr, reverse=True)
  # return arr

def get_best_sentence_for_ryhme(words_w_tags_and_similars):
  unmodified_l = []
  for (word,tag,similar_words) in words_w_tags_and_similars:
    #if len(similar_words) == 0:
    unmodified_l.append(word)

  rhym_cnt = get_rhym_distribution(get_pronounce_list_for_words(unmodified_l))

  modified_l = []

  for (word,tag,similar_words) in words_w_tags_and_similars:
    if len(similar_words) > 0:
      # arr = [(count[pair], pair) for pair in rhym_cnt]
      sim_word_selected = None
      max_value = -1
      max_key = None
      for w in similar_words:
        w = w.lower()
        p = None
        if w in cd:
          p = cd[w][0] # pick the first pronounciation
        else:
          continue
        key = None
        for i in range(len(p)-1, -1, -1):
          bit = p[i]
          if (bit[-1] == '1' or bit[-1] == '2' or bit[-1] == '0') and (bit != 'AH0'):
            key = (bit, len(p)-1-i)
            break

        if (key in rhym_cnt) and (rhym_cnt[key] > max_value):
          max_value = rhym_cnt[key]
          sim_word_selected = w
          max_key = key

      if sim_word_selected != None:
        rhym_cnt[max_key] += 1
        modified_l.append(sim_word_selected)
      else:
        modified_l.append(word)
    else:
      modified_l.append(word)

  return modified_l

def get_best_sentence_for_ryhme_smooth(words_w_tags_and_similars):
  unmodified_l = []
  for (word,tag,similar_words) in words_w_tags_and_similars:
    #if len(similar_words) == 0:
    unmodified_l.append(word)
  rhym_cnt = get_rhym_distribution(get_pronounce_list_for_words(unmodified_l))
  modified_l = []

  # pass 1
  # get the count for all possibles words and similar words
  for (word,tag,similar_words) in words_w_tags_and_similars:
    if len(similar_words) > 0:
      sim_words_tuple_list = set()
      for w in similar_words:
        w = w.lower()
        p = None
        if w in cd:
          p = cd[w][0] # pick the first pronounciation
        else:
          continue
        key = None
        for i in range(len(p)-1, -1, -1):
          bit = p[i]
          if (bit[-1] == '1' or bit[-1] == '2' or bit[-1] == '0') and (bit != 'AH0'):
            sim_words_tuple_list.add((bit, len(p)-1-i))
            break
      for tpl in sim_words_tuple_list:
        rhym_cnt[tpl] += 1.0

  arr = [(rhym_cnt[pair], pair) for pair in rhym_cnt]
  # DIFF: not sort from reverse
  arr = sorted(arr)

  # pass 2
  # select the similar words with highest rhyme frequency
  for (word,tag,similar_words) in words_w_tags_and_similars:
    if len(similar_words) > 0:
      hasAppend = False
      word_to_append = None
      word_idx = len(arr)
      for w in similar_words:
        w_tpl = None
        w = w.lower()
        p = None
        if w in cd:
          p = cd[w][0] # pick the first pronounciation
        else:
          continue
        for i in range(len(p)-1, -1, -1):
          bit = p[i]
          if (bit[-1] == '1' or bit[-1] == '2' or bit[-1] == '0') and (bit != 'AH0'):
            w_tpl = (bit, len(p)-1-i)
            for idx, tpl in enumerate(arr):
              if tpl[1] == w_tpl:
                if idx < word_idx:
                  word_idx = idx
                  word_to_append = w
                break
            break
      if word_to_append != None:
        modified_l.append(word_to_append)
        hasAppend = True

      if not hasAppend:
        modified_l.append(word)
        #modified_l.append(similar_words[int(random.random() * len(similar_words))])
    else:
      modified_l.append(word)

  return modified_l

def get_best_sentence_for_ryhme_highest(words_w_tags_and_similars):
  unmodified_l = []
  for (word,tag,similar_words) in words_w_tags_and_similars:
    #if len(similar_words) == 0:
    unmodified_l.append(word)

  rhym_cnt = get_rhym_distribution(get_pronounce_list_for_words(unmodified_l))

  modified_l = []

  # pass 1
  # get the count for all possibles words and similar words
  for (word,tag,similar_words) in words_w_tags_and_similars:
    if len(similar_words) > 0:
      sim_words_tuple_list = set()
      for w in similar_words:
        w = w.lower()
        p = None
        if w in cd:
          p = cd[w][0] # pick the first pronounciation
        else:
          continue
        key = None
        for i in range(len(p)-1, -1, -1):
          bit = p[i]
          if (bit[-1] == '1' or bit[-1] == '2' or bit[-1] == '0') and (bit != 'AH0'):
            sim_words_tuple_list.add((bit, len(p)-1-i))
            break
      for tpl in sim_words_tuple_list:
        rhym_cnt[tpl] += 1.0

  arr = [(rhym_cnt[pair], pair) for pair in rhym_cnt]
  arr = sorted(arr, reverse=True)

  # consider when arr is empty
  highest_tuple = None
  if len(arr) > 0:
    highest_tuple = arr[0][1]
    print ">>>>>> rhyme: ", highest_tuple

  # pass 2
  # select the similar words with highest rhyme frequency
  for (word,tag,similar_words) in words_w_tags_and_similars:
    if len(similar_words) > 0:
      hasAppend = False
      for w in similar_words:
        w_tpl = None
        w = w.lower()
        p = None
        if w in cd:
          p = cd[w][0] # pick the first pronounciation
        else:
          continue
        for i in range(len(p)-1, -1, -1):
          bit = p[i]
          if (bit[-1] == '1' or bit[-1] == '2' or bit[-1] == '0') and (bit != 'AH0'):
            w_tpl = (bit, len(p)-1-i)
            break
        if w_tpl != None and w_tpl == highest_tuple:
          modified_l.append(w)
          hasAppend = True
          break
      if not hasAppend:
        modified_l.append(word)
        #modified_l.append(similar_words[int(random.random() * len(similar_words))])
    else:
      modified_l.append(word)

  return modified_l

def get_stress_fluctuate(pron):
  # print "word: ", words
  # print "pron: ", pron
  count = collections.Counter()
  flag = None
  fluctuate = 0.0
  total = 0.0
  for p in pron:
    for bit in p:
      if bit[-1] == '1':
        if flag == 0: fluctuate += 1
        flag = 1
        total += 1
      elif bit[-1] == '0':
        if flag == 1: fluctuate += 1
        flag = 0
        total += 1
  # print "stress change: ", fluctuate / len(words)
  # print "\n"
  if total == 0: return 0
  return fluctuate


def get_best_sentence_for_stress_change(words_w_tags_and_similars):

  modified_l = []
  prev_word = None

  for (word,tag,similar_words) in words_w_tags_and_similars:
    if len(similar_words) > 0:
      # max_fluctuate = -1
      max_fluctuate = 10000
      max_fluctuate_list = None

      stress_cnt_dict = {}
      for sim_w in similar_words:
        w_new_list = [prev_word, sim_w] if prev_word != None else [sim_w]
        # print w_new_list
        words_pron = get_pronounce_list_for_words(w_new_list)
        score = get_stress_fluctuate(words_pron)

        if score < max_fluctuate:
        #if score > max_fluctuate:
          max_fluctuate = score
          max_fluctuate_list = [sim_w]
        elif score == max_fluctuate:
          max_fluctuate_list.append(sim_w)

      arr = [(-1.0*len(w), w) for w in max_fluctuate_list]
      arr = sorted(arr, reverse=True)
      word_picked = arr[0][1]
      prev_word = word_picked
      modified_l.append(word_picked)
      # if max_fluctuate_word != None:
      #   modified_l.append(max_fluctuate_word)
      #   prev_word = max_fluctuate_word
      # else:
      #   prev_word = word
      #   modified_l.append(word)
      #   #modified_l.append(similar_words[int(random.random() * len(similar_words))])
    else:
      prev_word = word
      modified_l.append(word)

  return modified_l


def print_original_modified_pair(words_w_tags_and_similars):
  words_list = []
  sentence_original = ""
  sentence_generated = ""
  for (word,tag,similar_words) in words_w_tags_and_similars:
    sentence_original += word + " "
    words_list.append(word)
    # if tag.startswith("JJ"):
    #   continue
    if len(similar_words) != 0:
      sentence_generated += similar_words[int(random.random() * len(similar_words))] + " "
    else:
      sentence_generated += word + " "
  # overwrite
  # sentence_generated = ' '.join(get_best_sentence_for_ryhme(words_w_tags_and_similars))
  words_gen_list = get_best_sentence_for_stress_change(words_w_tags_and_similars)
  # words_gen_list = get_best_sentence_for_ryhme_smooth(words_w_tags_and_similars)
  sentence_generated = ' '.join(words_gen_list)
  pron_gen = get_pronounce_list(words_gen_list)

  pron_original = get_pronounce_list(words_list)

  print sentence_original
  print pron_original
  print "\n"
  print sentence_generated
  print pron_gen
  print "\n\n"

def get_pronounce_list(words):
  pron = []
  for w in words:
    w = w.lower()
    if w in cd:
      pron.append(cd[w][0]) # pick the first pronounciation
  return pron

def processDir(subDir):
  filePath = './' + subDir
  files = os.listdir(filePath)
  #print files
  raw_files = []
  medium_article_hash = {}
  for f in files:
    if not f.endswith('txt'): continue
    if subDir == "medium_posts_divided":
      if f.split("_")[-1] not in medium_article_hash:
        medium_article_hash[f.split("_")[-1]] = True
      else:
        continue

    statinfo = os.stat(os.path.join(filePath, f))
    raw_files.append((statinfo.st_size, f))

  cap = 5000 # control traning variance and bias
  sorted_files = sorted(raw_files, reverse=True)
  sorted_files = sorted_files[0: cap]
  count = 0
  modified_docs = []
  original_docs = []
  for (size, f) in sorted_files:
    # print "(", size, f, ")"
    tpl = getWordsFromFile(filePath, f)
    if tpl == None: continue
    (_, words_w_tags) = tpl

    similar_words_attached = attach_similar_words(words_w_tags)
    modified_docs.append(get_best_sentence_for_stress_change(similar_words_attached))
    #modified_docs.append(get_best_sentence_for_ryhme_highest(similar_words_attached))
    if DEBUG:
      print_original_modified_pair(similar_words_attached)

    words = [word for word,tag in words_w_tags]
    original_docs.append(words)
  return (original_docs, modified_docs)

if DEBUG:
  processDir("medium_posts_divided")








