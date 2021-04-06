#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"

progName="collect-data-stats.sh"


function usage {
    echo
    echo "$progName: usage: $progName <input concept freq dir 1> [<input concept freq dir 2> ...]"
    echo
    echo "  Collects global stats by year for each 'concept freq' dir given a argument."
    echo "  Output on STDOUT."
    echo
    echo "  Options:"
    echo "    -h: print this help message."
    echo ""
}


while getopts 'h' option ; do
    case $option in
	"h" ) usage
	          exit 0;;
        "?" )
            echo "Error, unknow option." 1>&2
            usage 1>&2
	        exit 1
    esac
done
shift $(($OPTIND - 1)) # skip options already processed above
if [ $# -lt 1 ]; then
    echo "Error: at leat 1 argument expected." 1>&2
    echo 1>&2
    usage 1>&2
    exit 1
fi

inputDirs="$@"

echo -e "dataset\tyear\tview\tdocuments\tsentences\tconcepts_types\tconcepts_tokens"
for inputDir in $inputDirs; do
    dataset=$(basename "${inputDir%.*}")
    if [ ! -d "$inputDir" ]; then
	echo "Error: $inputDir doesn't exist" 1>&2
	exit 2
    fi
    for viewDir in "$inputDir"/by-doc/*; do
	view=$(basename "$viewDir")
	for docYearFile in "$viewDir"/????.total; do
	    year=$(cat "$docYearFile" | cut -f 1)
	    types=$(cat "$docYearFile" | cut -f 2)
	    docs=$(cat "$docYearFile" | cut -f 3)
	    tokens=$(cat "$docYearFile" | cut -f 4)
	    sentYearFile="$inputDir/by-sent/$view/$year.total"
	    if [ ! -s "$sentYearFile" ]; then
		echo "Bug" 1>&2
		exit 1
	    fi
	    sents=$(cat "$sentYearFile" | cut -f 3)
	    echo -e "$dataset\t$year\t$view\t$docs\t$sents\t$types\t$tokens"
	done
    done
done


