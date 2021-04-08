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


# patch for fixing invalid year such as ' 2020 ' (PTC)  or '02017' (KD)
# test cases:
# x=" 2020 "
# fixInvalidYear "$x"
# x="02017"
# fixInvalidYear "$x"
# x="00000"
# fixInvalidYear "$x"
# x="00324"
# fixInvalidYear "$x"
# x="1234"
# fixInvalidYear "$x"
function fixInvalidYear {
    year0=$(echo $1)
    if [ "${#year0}" -ne 4 ]; then
	year1=$(echo "$year0" | sed 's/^0*//')
	if [ -z "$year1" ]; then 
	    echo "0000"
	else
	    printf "%04d\n"  "$year1"
	fi
    else
	echo "$year0"
    fi
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
	    y0=${b%%.*}
	    y=$(fixInvalidYear "$y0")
	    # patch for invalid year needed for the next steps to correctly read the year from the filename 
	    # this is not ideal since it breaks the principle of keeping the same filename, but it's better than
	    # keeping the invalid year which causes bugs everywhere.
	    # Important: the original invalid year is kept additionally to the corrected version in order to avoid
	    # writing twice to the same output file (i.e. overwriting)
	    # ideally these cases should be fixed in the steps before.
	    if [ "$y" != "$y0" ]; then  
		b="$y.$b"
	    fi
	    python3 "$DIR"/build-doc-concept-matrix.py $optKD "$y" "$d" "${f%.cuis}" "$outputDir/by-$d/$cOUT/${b%.cuis}"
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
done
