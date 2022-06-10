#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://github.com/boudinfl/pke
# pip3 install --user --upgrade yaplon nltk spacy git+https://github.com/boudinfl/pke.git;
# python3 -m nltk.downloader stopwords
# python -m nltk.downloader universal_tagset
# python -m spacy download en

import glob
import os.path
import re
import sys
from collections import OrderedDict
import math

import sh
from pke.unsupervised import (ExpandRank, FirstPhrases, KPMiner, MultipartiteRank, PositionRank, TextRank, TfIdf,
                              TopicRank, TopicalPageRank, YAKE)
from yaplon import oyaml

mdtotext = sh.Command("./md-to-text.sh")


def getKeyphrasesFromModel(model, mbest, text):
    extractor = model()
    extractor.load_document(text, language='en')
    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases = extractor.get_n_best(n=mbest)
    print()
    print(model, mbest, keyphrases)
    return keyphrases


reKeyphrase = re.compile('[^A-Z ]+', re.IGNORECASE)


def processKeyphrase(text):
    return reKeyphrase.sub('', text, 0).replace('  ', ' ')


kill_list = [
    'font', 'fonts', 'glyph', 'glyphs', 'fontlab', 'window', 'panel', 'dialog', 'click', 'checkbox', 'would like', 'menu', 'drag', 'button', 'windows', 'panels', 'dialogs', 'clicking', 'buttons', 'command', 'bar', 'toggle', 'dropdown', 'mode', 'use', 'uses', 'menu command', 'info'
]


def filterKeyphrases(phrases):
    newphrases = []
    for phrase in phrases:
        if phrase not in kill_list:
            newphrases.append(phrase)
    return newphrases


def getKeyphrasesFromText(text):
    len_words=len(text.split(" "))
    print("# Words", len_words)
    mx=int((math.log(len_words,1.25)-9)/3)
    models = OrderedDict([
        (KPMiner, [mx*3, 1]),
        (TopicRank, [mx*3, 100]),
        (MultipartiteRank, [mx*3, 100]),
        (PositionRank, [mx*3, 25]),
        (TextRank, [mx, 5]),
        (TopicalPageRank, [mx*3, 5]),
    ])
    dkps = {}
    for m, mdata in models.items():
        mbest, weight = mdata
        try:
            mkps = getKeyphrasesFromModel(m, mbest, text)
        except:
            mkps = []
        # print(m, mkps)
        for kp, kv in mkps:
            if kp in dkps:
                dkps[kp] += kv*weight
            else:
                dkps[kp] = kv*weight
    keyphrases = filterKeyphrases([processKeyphrase(t[0]) for t in sorted(
        dkps.items(), key=lambda kv: kv[1], reverse=True)])
    return keyphrases[:mx]


def addKeyphrasesToMdFile(path):
    mdf = open(path, "r")
    line1 = mdf.readline()
    if line1 != '---\n':
        return False
    else:
        ytext = ""
        md = ""
        ismd = False
        for line in mdf.readlines():
            if line == '---\n':
                ismd = True
            if ismd:
                md += line
            else:
                ytext += line
    mdf.close()
    print()
    print("---------")
    print("Processing: %s" % (os.path.split(path)[1]))
    try:
        mdtext = str(mdtotext(path))
        keyphrases = getKeyphrasesFromText(mdtext)
        print()
        print("### Keyphrases:")
        print("    %s" % (", ".join(keyphrases)))
    except:
        pass
    try:
        ydata = oyaml.read_yaml(ytext)
        #if 'topic-tags' in ydata: del ydata['topic-tags']
        #if 'tags' in ydata: del ydata['tags']
        #if 'autotags' in ydata: del ydata['autotags']
        ydata['topic-auto'] = keyphrases
        ynew = oyaml.yaml_dumps(ydata)
        mdnew = '---\n' + ynew + md
        with open(path, 'w') as mdf:
            mdf.write(mdnew)
        return True
    except:
        return False


def addKeyPhrasesToMdFolder(folder):
    paths = glob.glob(os.path.join(folder, '*.md'))
    for path in paths:
        if addKeyphrasesToMdFile(path):
            print("Saved: %s" % (os.path.split(path)[1]))
            print()


print("Usage: addkeyphrasestomd.py [folder]")
if len(sys.argv) > 1:
    folder = sys.argv[1]
else:
    folder = "../wiki/"
addKeyPhrasesToMdFolder(folder)
print("Finished!")
