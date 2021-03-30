#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"

levels="by-doc by-sent"

processDirs="filtered-medline pmc-abstracts pmc-articles"
kdDirs="abstracts+articles/abstracts abstracts+articles/articles unfiltered-medline"
outputDirs="unfiltered-medline pmc-articles abstracts+articles"
kdData=""

function checkDirs {
    topDir="$1"
    dirs="$2"
    for d in $dirs; do
	if [ ! -d "$topDir/$d" ]; then
	    return 1
	fi
    done
    return 0
}


if [ $# -ne 2 ]; then
    echo "Usage: <input dir> <output dir>" 1>&2
    echo 1>&2
    echo "  Reads data by year from all the input dirs provided."
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

for level in $levels; do
    echo "Info: level = '$level'" 1>&2
    mkdir "$outputDir/$level"
    if checkDirs "$inputDir/$level"  "$processDirs"; then
	echo "Info: regular dirs '$processDirs' found." 1>&2
    else
	echo "Info: regular dirs '$processDirs' not all found, testing KD dirs = '$kdDirs'" 1>&2
	if checkDirs "$inputDir/$level" "$kdDirs"; then
	    processDirs="$kdDirs"
	    echo "dirs = '$processDirs' ok" 1>&2
	    kdData=1
	else
	    echo "Error: dirs '$kdDirs' not found either, aborting" 1>&2
	    exit 1
	fi
    fi

    for outDir in $outputDirs; do
	echo "$level / $outDir"
	d="$outputDir/$level/$outDir"
	mkdir "$d"

	if [ "$outDir" == "unfiltered-medline" ]; then
	    if [ -z "$kdData" ]; then
		inDirs="filtered-medline pmc-abstracts"
	    else
		inDirs="unfiltered-medline"
	    fi
	elif [ "$outDir" == "pmc-articles" ]; then
	    if [ -z "$kdData" ]; then
		inDirs="pmc-articles"
	    else
		inDirs="abstracts+articles/articles"
	    fi
	elif [ "$outDir" == "abstracts+articles" ]; then
	    if [ -z "$kdData" ]; then
		inDirs="filtered-medline pmc-articles"
	    else
		inDirs="abstracts+articles/abstracts abstracts+articles/articles"
	    fi
	else
	    echo "BUG" 1>&2
	    exit 1
	fi

	all=""
	for inDir in $inDirs; do
	    d="$inputDir/$level/$inDir"
	    if [ ! -d "$d" ]; then
		echo "Error: no dir '$d'" 1>&2
		exit 1
	    else
		all="$all $d/REPLACE"
	    fi
	done
	allLS=$(echo "$all" | sed 's:REPLACE:*:g')
	ls $allLS | while read f; do
	    b=$(basename "$f")
	    y=${b%%.*}
	    echo "$y"
	done | while read year; do
	    yearLS=$(echo "$all" | sed "s:REPLACE:$year\*:g")
	    echo "ls $yearLS | python3 $DIR/get-frequency-from-doc-concept-matrix.py \"$d/$year\""
	    ls $yearLS | python3 $DIR/get-frequency-from-doc-concept-matrix.py "$d/$year"
	    exit 1
	done
	
    done
    
done

