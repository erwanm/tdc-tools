#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"

progName="get-frequency-from-doc-concept-matrix-single-dir.sh"


function usage {
    echo
    echo "$progName: usage: echo <input dir1> [input dir 2] ... | $progName <output dir> [target concepts]"
    echo
    echo "  This script runs get-frequency-from-doc-concept-matrix.py for every year"
    echo "  for a single output dir (no level or 'data view'). A particular year is "
    echo "  obtained by merging it from the different input directories."
    echo
    echo "  See details in get-frequency-from-doc-concept-matrix.py."
    echo
    echo "  Options:"
    echo "    -h: print this help message."
    echo "    -o '<options>' options for get-frequency-from-doc-concept-matrix.py, e.g."
    echo "        '-j -p -v <groups>': see details in get-frequency-from-doc-concept-matrix.py."
    echo "    -w write commands to STDOUT instead of executing them."
    echo ""
}


 
options=""
printCommands=""
while getopts 'ho:w' option ; do
    case $option in
	"h" ) usage
	          exit 0;;
	"o" )  options="$OPTARG";;
	"w" ) printCommands=1;;
        "?" )
            echo "Error, unknow option." 1>&2
            usage 1>&2
	        exit 1
    esac
done
shift $(($OPTIND - 1)) # skip options already processed above
if [ $# -ne 1 ] && [ $# -ne 2 ]; then
    echo "Error: 1 or 2 arguments expected." 1>&2
    echo 1>&2
    usage 1>&2
    exit 1
fi

outputDir="$1"
targetsFile="$2"

[ -d "$outputDir" ] || mkdir "$outputDir"


#line=$(read)
#set -- $line

all=""
while read line; do
    # read STDIN and assigns positional parameters from it
    set -- $line
    while [ $# -ne 0 ]; do
	inDir="$1"
	if [ ! -d "$inDir" ]; then
	    echo "Error: no dir '$inDir'" 1>&2
	    exit 1
	else
	    all="$all $inDir/REPLACE"
	fi
	shift
    done
done

allLS=$(echo "$all" | sed 's:REPLACE:*:g')
ls $allLS | while read f; do
    b=$(basename "$f")
    y=${b%%.*}
    echo "$y"
done | sort -u | while read year; do
    yearLS=$(echo "$all" | sed "s:REPLACE:$year\*:g")
    command="ls $yearLS 2>/dev/null | python3 $DIR/get-frequency-from-doc-concept-matrix.py $options \"$outputDir/$year\" $targetsFile 2>\"$outputDir/$year.err\"" 
    if [ -z "$printCommands" ]; then
	eval "$command"
	if [ $? -ne 0 ]; then
	    echo "Error with command:" 1>&2
	    echo "$command" 1>&2
	    exit 1
	fi
    else
	echo "$command"
    fi
done
	
