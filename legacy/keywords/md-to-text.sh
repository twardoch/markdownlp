#!/usr/bin/env bash

dir=${0%/*}
if [ "$dir" = "$0" ]; then
  dir="."
fi
cd "$dir"

cat $1 | remark -S -r ./remarkrc.js -u html | html-to-text --wordwrap=false --noLinkBrackets=true --ignoreHref=true --ignoreImage=true --uppercaseHeadings=false --unorderedListItemPrefix='-' | sed 's/!!! //g'
