#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"

processDirs="filtered-medline pmc-abstracts pmc-articles"
kdDirs="abstracts+articles/deduplicated.disambiguated/abstracts abstracts+articles/deduplicated.disambiguated/articles unfiltered-medline/deduplicated.disambiguated"


function checkDirs {
    dirs="$1"
    for d in $dirs; do
	if [ ! -d "$inputDir/$d" ]; then
	    return 1
	fi
    done
    return 0
}

optKD=""
if [ "$1" == "-k" ]; then
    optKD="-k"
    echo "Info: KD option ON." 1>&2
    shift
else
    echo "Info: KD option OFF." 1>&2
fi

if [ $# -ne 2 ]; then
    echo "Usage: [-k] <input TDC dir> <output dir>" 1>&2
    echo "" 1>&2
    echo "   -k: multiple concepts separated by comma (KD data format)" 1>&2
    exit 1
fi

inputDir="$1"
outputDir="$2"

if [ -d "$outputDir" ]; then
    echo "Warning: $outputDir already exists, possible previous content" 1>&2
fi

[ -d "$outputDir" ] || mkdir "$outputDir"

if [ ! -d "$inputDir" ]; then
    echo "Error: $inputDir doesn't exist" 1>&2
    exit 2
fi

if checkDirs  "$processDirs"; then
    echo "Info: regular dirs '$processDirs' found." 1>&2
else
    echo "Info: regular dirs '$processDirs' not all found, testing KD dirs = '$kdDirs'" 1>&2
    if checkDirs  "$kdDirs"; then
	processDirs="$kdDirs"
	echo "dirs = '$processDirs' ok" 1>&2
    else
	echo "Error: dirs '$kdDirs' not found either, aborting" 1>&2
	exit 1
    fi
fi


for d in doc sent; do 
    mkdir "$outputDir/by-$d"
    for c in $processDirs; do
	cOUT=$(echo "$c" | sed 's:/deduplicated.disambiguated::g')
	echo "$d / $cOUT"
	mkdir -p "$outputDir/by-$d/$cOUT"
	ls "$inputDir"/$c/*cuis | while read f ; do   
	    b=$(basename "$f")
	    y=${b%%.*}
	    python3 "$DIR"/build-doc-concept-matrix.py $optKD "$y" "$d" "${f%.cuis}" "$outputDir/by-$d/$cOUT/${b%.cuis}"
	done
    done
done

