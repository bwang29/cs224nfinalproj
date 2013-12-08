# encoding: utf-8

import sys, os, shutil, time, argparse, datetime
import collections
import math
import numpy
import random
import re
import readline
import nltk
import modify

from nltk.corpus import cmudict
from nltk.corpus import wordnet as wn
from sklearn import svm
from sklearn import metrics
from sklearn.naive_bayes import GaussianNB

cd = cmudict.dict()

trainDocs = []
trainLabels = []

testDocs = []
testLabels = []

# global variables for tuning
sentences_len_list = range(3,4)
NUM_SENTENCES = 3
INCLUDE_LENGTH = False #SL
INCLUDE_STRESS_COUNT = False #RSL
INCLUDE_RYHME = False #SDS
INCLUDE_RYHME_TAIL = False #CMCS
INCLUDE_STRESS_CHANGE = True #SF
INCLUDE_WORD_LEN_MEAN = False #AWL
INCLUDE_WORD_LEN_STD = False #SD

INCLUDE_RANDOM = False


TEST_SINGLE = True
# TODO
# given a list of words and punctuations, extract feature vector
def extractFeature(words):
  pron = get_pronounce_list(words)

  word_length = len(words)
  (count1, count2, count3) = primary_secondary_stress_ratio(words, pron)
  ryhme_count = rhym_distribution(words, pron)
  ryhme_tail = rhym_naive(words)
  stress_change = stress_change_count(words, pron)
  (word_len_mean, word_len_std) = word_length_deviation(words)

  fv = []
  if INCLUDE_LENGTH: fv.append(word_length)
  if INCLUDE_STRESS_COUNT: fv += list((count1, count2, count3))
  if INCLUDE_RYHME: fv.append(ryhme_count)
  if INCLUDE_RYHME_TAIL: fv.append(ryhme_tail)

  if INCLUDE_STRESS_CHANGE: fv.append(stress_change)

  if INCLUDE_RANDOM: fv.append(random.random())

  if INCLUDE_WORD_LEN_MEAN: fv.append(word_len_mean)
  if INCLUDE_WORD_LEN_STD: fv.append(word_len_std)

  return fv

def get_pronounce_list(words):
  pron = []
  for w in words:
    w = w.lower()
    if w in cd:
      pron.append(cd[w][0]) # pick the first pronounciation
  return pron

def word_length_deviation(words):
  word_length = [len(w) for w in words]
  mean = numpy.mean(word_length)
  std = numpy.std(word_length)
  return (mean, std)

def primary_secondary_stress_ratio(words, pron):
  # print "word: ", words
  # print "pron: ", pron
  count = collections.Counter()
  for p in pron:
    for bit in p:
      if bit[-1] == '1': count[1] += 1
      elif bit[-1] == '0': count[0] += 1
      elif bit[-1] == '2': count[2] += 1
      else: count[-1] += 1
  return (float(count[0]+1)/float(count[2]+1), float(count[1]+1)/float(count[2]+1), float(count[1]+1)/float(count[0]+1))

def stress_change_count(words, pron):
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
  return fluctuate / len(words)

def rhym_naive(words):
  selected_words = []
  for idx, w in enumerate(words):
    if idx < len(words)-1:
      if words[idx+1] == '.': selected_words.append(w)
  pron = get_pronounce_list(selected_words)

  count = collections.Counter()
  for p in pron:
    for i in range(len(p)-1, -1, -1):
      bit = p[i]
      if (bit[-1] == '1' or bit[-1] == '2' or bit[-1] == '0'):
        count[(bit, len(p)-1-i)] += 1.0

        # if i != len(p) -1:
        #   count[(bit, p[i+1],len(p)-1-i)] += 1.0
        break

  arr = [(count[pair], pair) for pair in count]
  arr = sorted(arr, reverse=True)
  if len(arr) < 1: return 0.0
  return arr[0][0]
  #     # return (float(arr[0][0]) - float(arr[1][0])) / len(words)
  # return (float(arr[0][0])) / len(words)


def rhym_distribution(words, pron):
  # print "================== + ==================\n"
  # print "words: ", words
  # print "pron : ", pron
  count = collections.Counter()
  for p in pron:
    for i in range(len(p)-1, -1, -1):
      bit = p[i]
      if (bit[-1] == '1' or bit[-1] == '2' or bit[-1] == '0'):
        count[(bit, len(p)-1-i)] += 1.0
        break
  arr = [(count[pair], pair) for pair in count]
  arr = sorted(arr, reverse=True)
  arr_val = []
  for i in range(0, len(arr)):
    # if len(arr) < i+1: break
    # print arr[i][0], " >>> ", arr[i][1]
    arr_val.append(arr[i][0])
  res = numpy.std(arr_val) if len(arr_val) > 0 else 0
  # #print "std: ", res
  if math.isnan(res):
    res = 0 # array length might be 0
  # return res
  # print "sorted: ", arr
  # print "\n"
  return res
  #if len(arr) < 2: return 0.0
      # return (float(arr[0][0]) - float(arr[1][0])) / len(words)
  #return (float(arr[0][0])) / len(words)

  # if len(arr) < 3:
  #   return 0
  # nom = arr[0][0] + arr[1][0]
  # denom = 0.0
  # for (c, _) in arr:
  #   denom += c
  # return float(nom)/(denom-nom)

  # print count[1], " >>> ", float(count[1])/(float(count[2])+1)
  # return (float(count[0]+1)/float(count[2]+1), float(count[1]+1)/float(count[2]+1), float(count[1]+1)/float(count[0]+1))
  # print "===== counter: ", count[1]
  # print "\n"

# train svm model
def svmTrain(X, y):
  # clf = svm.SVC(kernel='linear')
  clf = svm.SVC()
  # clf = GaussianNB()
  clf.fit(X, y)
  #print ">>>>> svm coef: ", clf.coef_
  return clf

# get a tuple of (doc_name, list_of_words, label) from a given file
def getWordsFromFile(filePath, fileName, label):
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

  # tokens = []
  # for s in sentences[start:start + NUM_SENTENCES]:
  #   tokens += nltk.word_tokenize(s+" . ")

  # print tokens
  # print "\n"

  split = '.'
  docBody = split.join(sentences[start:start + NUM_SENTENCES]) + '.'
  docBody = docBody.replace("’","'")
  # print docBody

  tokens_ours = re.findall(r"[\w']+|[.,!?;]", docBody)
  # print tokens_ours
  # print "\n\n\n"
  # return (docName, re.findall(r"[\w']+|[.,!?;]", docBody), label)
  return (docName, tokens_ours, label)

def train():
  docs = [extractFeature(doc) for doc in trainDocs]
  return svmTrain(docs, trainLabels)


def test(model):
  labels = testLabels
  test_docs_fv = [extractFeature(words) for words in testDocs]
  predicted = model.predict(test_docs_fv)

  print "------------------------ results  ------------------------"
  print metrics.classification_report(labels, predicted)

  poem_length = []
  medium_length = []
  for idx in range(0, len(testDocs)):
    if labels[idx] != predicted[idx]:
      (gold, prec) = ('poem', 'medium') if labels[idx] == 1 else ('medium', 'poem')
      print "doc: ", ' '.join(testDocs[idx])
      print "gold: ", gold, " >>>>>> ", "predict: ", prec
      if labels[idx] == 1: poem_length.append(len(testDocs[idx]))
      if labels[idx] == 0: medium_length.append(len(testDocs[idx]))

  print "[misclassified] poem length: ", numpy.mean(poem_length)
  print "[misclassified] medium length: ", numpy.mean(medium_length)

  # cnt_pos, cnt_neg, total_pos, total_neg = 0.0, 0.0, 0.0, 0.0
  # medium_as_poem = 0
  # for idx in range(0, len(testDocs)):
  #   if labels[idx] == 1:
  #     total_pos += 1.0
  #     if predicted[idx] == 1:
  #       cnt_pos += 1.0
  #   else:
  #     total_neg += 1.0
  #     if predicted[idx] == 0:
  #       cnt_neg += 1.0
  #     else:
  #       medium_as_poem += 1
  # print "before modified: ", medium_as_poem
  # print "positive accuracy: ", cnt_pos/total_pos, " out of ", total_pos, " test poems"
  # print "negative accuracy: ", cnt_neg/total_neg, " out of ", total_neg, " test mediums"

def testSingle(model, docBody):
  docBody = docBody.replace("’","'")
  words = re.findall(r"[\w']+|[.,!?;]", docBody)
  predicted = model.predict([extractFeature(words)])

  res = 'poem' if predicted[0] == 1 else 'medium'
  print docBody
  print ">>>> ", res
  print '\n'

def test_modify(model):
  (original_docs, modified_docs) = modify.processDir("medium_posts_divided")
  original_docs_fv = [extractFeature(words) for words in original_docs]
  modified_docs_fv = [extractFeature(words) for words in modified_docs]
  original_predicted = model.predict(original_docs_fv)
  modified_predicted = model.predict(modified_docs_fv)

  diff_count = 0
  diff_succ = 0
  for idx,label in enumerate(original_predicted):
    if label != modified_predicted[idx]:
      print "===== Original ====== "
      print ' '.join(original_docs[idx])
      print "===== Modified ====== "
      print ' '.join(modified_docs[idx])
      print "orignal: %d    =====>  modified: %d " % (label, modified_predicted[idx])
      print "\n"
      diff_count += 1
      if label == 0: diff_succ += 1
  print "diff_count: ", diff_count
  print "successful: ", diff_succ


stress_cnt_poem = []
stress_cnt_medium = []

def processDir(subDir, label):
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

  cap = 4000 # control traning variance and bias
  sorted_files = sorted(raw_files, reverse=True)
  sorted_files = sorted_files[0: cap]
  count = 0
  for (size, f) in sorted_files:
    # print "(", size, f, ")", label
    tpl = getWordsFromFile(filePath, f, label)
    if tpl == None: continue
    (_, words, label) = tpl

    docs = testDocs
    labels = testLabels
    if count % 10 > 0:
    #if random.random() < 0.9:
      docs = trainDocs
      labels = trainLabels
    count = (count + 1) % 10
    #fv = extractFeature(words)
    #docs.append(fv)
    docs.append(words)
    labels.append(label)
    # if label == 1: stress_cnt_poem.append(fv[0])
    # else: stress_cnt_medium.append(fv[0])

def seperateFiles():
  processDir('poems_normalized_divided', 1)
  # print "================ end of processing poems ================ "
  processDir('medium_posts_divided', 0)
  # print "============= end of processing medium posts ============ "

def dumpFeatureConfig():
  # print "================ feature configuration =================="
  feat = []
  if INCLUDE_LENGTH: feat.append('word_length')
  if INCLUDE_STRESS_COUNT: feat.append('3_stress_counts')
  if INCLUDE_RYHME: feat.append('ryhme')
  if INCLUDE_RANDOM: feat.append('random')
  if INCLUDE_STRESS_CHANGE: feat.append('stress_change')
  if INCLUDE_WORD_LEN_MEAN: feat.append('word_len_mean')
  if INCLUDE_WORD_LEN_STD: feat.append('word_len_std')
  if INCLUDE_RYHME_TAIL: feat.append('rhyme_tail_count')

  print "num of sentences: ", NUM_SENTENCES
  print "feature vector  : ", feat

if __name__ == '__main__':
  for i in sentences_len_list:
    trainDocs, trainLabels = [], []
    testDocs, testLabels = [], []
    NUM_SENTENCES = i
    dumpFeatureConfig()
    seperateFiles()
    print "train size: ", len(trainDocs)
    print "test size : ", len(testDocs)
    model = train()
    #test(model)
    test_modify(model)
    print "=========================================================="

    txt = "I am a frightened girl they don’t know I am.  I am a sad girl who cries at night behind close doors.  I am a distant girl who’s out of sight form the public eye.  "

    if TEST_SINGLE: testSingle(model, txt)

  # print "poem mean: ", numpy.mean(stress_cnt_poem), "std: ", numpy.std(stress_cnt_poem)
  # print "medium mean: ", numpy.mean(stress_cnt_medium), "std: ", numpy.std(stress_cnt_medium)








