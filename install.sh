#!/usr/bin/env bash
python3 -m pip install --user --upgrade keybert[spacy]
python3 -m spacy download en_core_web_lg

brew upgrade node
npm i -g npm@latest && npm audit fix

npm i -g html-to-text
chmod gou+x "${HOME}/.npm-packages/bin/html-to-text"


remark-cli
unified-args
npm i -g bobalu113/remark-wiki-link
