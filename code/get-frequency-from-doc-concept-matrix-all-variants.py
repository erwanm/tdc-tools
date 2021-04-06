#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"

levels="by-doc by-sent"

processDirs="filtered-medline pmc-abstracts pmc-articles"
kdDirs="abstracts+articles/abstracts abstracts+articles/articles unfiltered-medline"
outputDirs="unfiltered-medline pmc-articles abstracts+articles"
kdData=""


function usage {
    echo
    echo "$progName: usage: $progName <input dcm dir> <output dir> [target concepts]"
    echo
    echo "  This script runs get-frequency-from-doc-concept-matrix.py for every year,"
    echo "  every level and every 'data view'. "
    echo "  It deals automatically with the different set of input directories."
    echo
    echo "  See details in get-frequency-from-doc-concept-matrix.py."
    echo
    echo "  Options:"
    echo "    -h: print this help message."
    echo "    -j, -J, -p: see details in get-frequency-from-doc-concept-matrix.py."
    echo "    -w write commands to STDOUT instead of executing them"
    echo ""
}


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


options=""
printCommands=""
while getopts 'hjJpw' option ; do
    case $option in
	"h" ) usage
	          exit 0;;
	"j" | "J" | "p" )  options="$options -$option";;
	"w" ) printCommands=1;;
        "?" )
            echo "Error, unknow option." 1>&2
            usage 1>&2
	        exit 1
    esac
done
shift $(($OPTIND - 1)) # skip options already processed above
if [ $# -ne 2 ] && [ $# -ne 3 ]; then
    echo "Error: 2 or 3 arguments expected." 1>&2
    echo 1>&2
    usage 1>&2
    exit 1
fi

inputDir="$1"
outputDir="$2"
targetsFile="$3"

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
	fullOutDir="$outputDir/$level/$outDir"
	mkdir "$fullOutDir"

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
	    fullInDir="$inputDir/$level/$inDir"
	    if [ ! -d "$fullInDir" ]; then
		echo "Error: no dir '$fullInDir'" 1>&2
		exit 1
	    else
		all="$all $fullInDir/REPLACE"
	    fi
	done
	echo "$level / $outDir: input dirs = '$all', output = $fullOutDir" 1>&2
	allLS=$(echo "$all" | sed 's:REPLACE:*:g')
	ls $allLS | while read f; do
	    b=$(basename "$f")
	    y=${b%%.*}
	    echo "$y"
	done | sort -u | while read year; do
	    yearLS=$(echo "$all" | sed "s:REPLACE:$year\*:g")
	    command="ls $yearLS 2>/dev/null | python3 $DIR/get-frequency-from-doc-concept-matrix.py $options \"$fullOutDir/$year\" $targetsFile 2>\"$fullOutDir/$year.err\"" 
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
	if [ $? -ne 0 ]; then
	    exit 1
	fi
	
    done
    if [ $? -ne 0 ]; then
	exit 1
    fi
    
done
if [ $? -ne 0 ]; then
    exit 1
fi

