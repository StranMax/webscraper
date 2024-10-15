#!/bin/bash

files="$(find filelists/ -name '*.txt' -type f)"

for file in $files; do
  name=${file##*/}
  name=${name%.txt}
  name=${name/filelist_/''}
  mkdir -p $name
  wget -i $file -P $name
done

