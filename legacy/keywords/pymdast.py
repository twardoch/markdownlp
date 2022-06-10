#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# cat $1 | remark -S -r wiki/.remarkrc.yml -u html | html-to-text --wordwrap=false --noLinkBrackets=true --ignoreHref=true --ignoreImage=true --uppercaseHeadings=false --unorderedListItemPrefix='-' | sed 's/!!! //g'

import sh
import sys
import os.path
import collections
import json as jsonmod
import yaml as yamlmod
import fire

class Remark(object):

    tooldir = os.path.split(os.path.realpath(__file__))[0]

    def __init__(self):
        pass

    def _loadsMarkdown(self, md):
        shmd2json = sh.Command(os.path.join(self.tooldir,"md2json"))
        json = str(shmd2json(_in=md))
        self.json = json
        return self.json

    def _dumpsMarkdown(self, json=None):
        shjson2md = sh.Command(os.path.join(self.tooldir,"json2md"))
        if json: self.json = json
        if not self.json:
            if self.ast: self._getJsonFromAst()
        md = str(shjson2md(_in=self.json))
        self.md = md
        return self.md

    def _getAstFromJson(self, json=None):
        if json: self.json = json
        self.ast = jsonmod.loads(self.json, object_pairs_hook=collections.OrderedDict)
        return self.ast

    def _getJsonFromAst(self, ast=None):
        if ast: self.ast = ast
        self.json = jsonmod.dumps(self.ast)
        return self.json

    def _getYamlFromAst(self, ast=None):
        if ast: self.ast = ast
        if not self.ast:
            if self.json: self._getAstFromJson()
        tryYaml = self.ast['children'][0]
        if tryYaml['type'] == 'yaml':
            self.yaml = tryYaml['value']
        return self.yaml

    def _getMetaFromYaml(self, yaml=None):
        if yaml: self.yaml = yaml
        if not self.yaml:
            if self.ast: self._getYamlFromAst()
        self.meta = yamlmod.load(self.yaml, Loader=yamlmod.FullLoader)
        return self.meta

    def md2json(self, md=None):
        """Read Markdown from --md or stdin, output Remark AST as JSON"""
        mdfile = open(md, 'r') if md else sys.stdin
        return self._loadsMarkdown(md=mdfile.read())

    def md2meta(self, md=None):
        """Read Markdown from --md or stdin, output YAML frontmatter as string"""
        mdfile = open(md, 'r') if md else sys.stdin
        self._loadsMarkdown(md=mdfile.read())
        self._getAstFromJson()
        self._getYamlFromAst()
        return self._getMetaFromYaml()

    def json2md(self, json=None):
        """Read Remark AST JSON from --json or stdin, output Markdown"""
        jsonfile = open(json, 'r') if json else sys.stdin
        self._getAstFromJson(json=jsonfile.read())
        return self._dumpsMarkdown()

if __name__ == '__main__':
    fire.Fire(Remark)
