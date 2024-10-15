#! /bin/bash

while getopts m:f:s: flag
do
    case "${flag}" in
        m) metadata_dir=${OPTARG};;
        f) filelist_dir=${OPTARG};;
        s) suffix=${OPTARG};;
    esac
done

pattern=(
  "[Mm]aa[-]?seu.*"
  "[Hh]aja-asut.*"
  "\"[Hh]arvaan asut.*\""
  "[Ss]yrjä[-]?seu.*"
  "[Kk]yl[iä].*"
  "[Rr]euna-alu.*"
  "[Ss]yrjä[-]?alu.*"
  "[Rr]aja[-]?seu.*"
  "[Rr]aja-alu.*"
  "\"[Kk]aupunkien ulko[-]?puol.*\""
  "[Pp]aikalli.*"
  "[Aa]lueelli.*"
  "[Kk]aupun.*"
  "[Kk]eskus[-]?"
  "[Tt]aajama"
  "[Uu]rbaan.*"
  "[Ll]ähiö.*"
)
name=(
  "maaseutu"
  "haja-asutus"
  "harvaan_asuttu"
  "syrjäseutu"
  "kylä"
  "reuna-alue"
  "syrjäalue"
  "rajaseutu"
  "raja-alue"
  "kaupunkien_ulkopuolinen"
  "paikallinen"
  "alueellinen"
  "kaupunki"
  "keskus"
  "taajama"
  "urbaani"
  "lähiö"
)

mkdir -p $metadata_dir
mkdir -p $filelist_dir

for index in ${!pattern[*]}; do 
  oai-harvest https://julkaisut.valtioneuvosto.fi/oai/request -sp "${pattern[$index]}" -vv -m ${metadata_dir}/metadata_${name[$index]}_${suffix}.csv -f ${filelist_dir}/filelist_${name[$index]}_${suffix}.txt
done
