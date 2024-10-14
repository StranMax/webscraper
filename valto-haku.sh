#! /bin/bash

pattern=( \
  [Hh]aja-asut.* \
  [Hh]arvaan asut.* \
  [Ss]yrjä[-]?seu.* \
  [Kk]yl[iä].* \
  [Rr]euna-alu.* \
  [Rr]aja[-]?seu.* \
  [Kk]aupunkien ulko[-]?puol.* \
  [Pp]aikalli.* \
  [Aa]lueelli.* \
)
name=(
  haja-asutus
  harvaan_asuttu
  syrjäseutu
  kylä
  reuna-alue
  rajaseutu
  kaupunkien_ulkopuolinen
  paikallinen
  alueellinen
)
for index in ${!pattern[*]}; do 
  oai-harvest https://julkaisut.valtioneuvosto.fi/oai/request -sp ${pattern[$index]} -vv -m ../../metadatafiles/metadata_${name[$index]}_14102024.csv -f ../../filelists/filelist_${name[$index]}_14102024.txt
done
