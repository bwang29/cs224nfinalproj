import sys, os, shutil, time, argparse, datetime
import readline
import re
import random
import collections
from nltk.corpus import cmudict
from nltk.corpus import wordnet as wn

cd = cmudict.dict()

from sklearn import svm

trainPath = './data/'
testPath = './test/'

trainDocs = []
trainLabels = []

testDocs = []
testLabels = []

test_file = open('data.js', 'w')
param = {}
param['isLast'] = False

# TODO
# given a list of words and punctuations, extract feature vector
def extractFeature(words):
  pron = get_pronounce_list(words)
  rhym_distribution(words, pron)

def get_pronounce_list(words):
  pron = []
  for i in range(0, len(words)):
  #for w in words:
    w = words[i]
    w = w.lower()
    if w in cd:
      pron.append(cd[w][0]) # pick the first pronounciation
  return pron

def rhym_distribution(words, pron):
  #print "words: ", words
  pron_text = ""
  test_file.write("{")
  count = collections.Counter()
  for p in pron:
    for bit in p:
      pron_text += bit + " "
      if bit[-1] == '1' or bit[-1] == '2':
        count[bit] += 1.0
    pron_text += ", "
  arr = [(count[bit], bit) for bit in count]
  arr = sorted(arr, reverse=True)
  arr.append( ( "\""+" ".join(words).replace("\"","''")+"\"", "text" ) )
  arr.append( ("\""+pron_text+"\"", "pron") )
  # print " ".join(words).replace("\"","''")
  # print "\n"
  # for i in range(0, 10):
  for i in range(0, len(arr)):
    if len(arr) < i+1: break
    # print arr[i][0], " >>> ", arr[i][1]
    test_file.write('{0}{1}:{2}'.format(',' if i > 0 else '', arr[i][1], arr[i][0]))
  #test_file.write(',{0}:{1}'.format(, arr[i][0]))
  test_file.write('}')
  if not param['isLast']: test_file.write(',')
  # print count[1], " >>> ", float(count[1])/(float(count[2])+1)
  # return (float(count[0]+1)/float(count[2]+1), float(count[1]+1)/float(count[2]+1), float(count[1]+1)/float(count[0]+1))
  # print "===== counter: ", count[1]
  # print "\n"

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

  if len(sentences) < 5:
    return None

  # start = random.randint(0, len(sentences) - 4)
  # deterministic version
  start = (len(sentences) - 4)/2

  f.close()
  split = '.'
  docBody = split.join(sentences[start:start+3]) + '.'
  #print docBody
  return (docName, re.findall(r"[\w']+|[.,!?;]", docBody), label)

# read all poems(.txt files) of the given filePath
def processFiles(filePath, docs, labels):
  files = os.listdir(filePath)
  #debug
  len_list = []
  #print files
  for f in files:
    if not f.endswith('txt'): continue
    tpl = getWordsFromFile(filePath, f)
    if tpl == None: continue
    (_, words, label) = tpl
    #print words, label
    #print '\n'
    docs.append(extractFeature(words))
    labels.append(label)
    len_list.append(len(words))
  print "filePath: ", filePath, " average doc length: ", sum(len_list)*1.0/len(len_list)

def processDir(subDir, label):
  filePath = './' + subDir
  files = os.listdir(filePath)
  #print files
  raw_files = []
  for f in files:
    if not f.endswith('txt'): continue
    statinfo = os.stat(os.path.join(filePath, f))
    raw_files.append((statinfo.st_size, f))

  cap = 500 # control traning variance and bias
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
    count = count + 1
    if (count == len(sorted_files)): param['isLast'] = True
    docs.append(extractFeature(words))
    labels.append(label)

  param['isLast'] = False

def seperateFiles():
  test_file.write("var data_poem = [")
  processDir('poems_normalized_divided', 1)
  test_file.write("]\nvar data_post = [")
  print " =================================== "
  processDir('medium_posts_divided', 0)
  test_file.write("]")
  test_file.close()

if __name__ == '__main__':
  seperateFiles()






