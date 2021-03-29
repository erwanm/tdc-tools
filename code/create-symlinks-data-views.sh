#!/bin/bash


function createLinks {
    local sourceDir="$1"
    local id="$2"

    echo "Creating links to $sourceDir in $(pwd)..." 1>&2
    for f in ../"$sourceDir"/*; do
	n=$(basename "${f%.*}")
	s="${f##*.}"
	ln -s "$f" "$n-$id.$s"
    done
}


if [ $# -ne 1 ]; then
    echo "Usage: $0 <PTC TDC output dir>" 1>&2
    echo 1>&2
    echo "  The directory must contain the three subdirectories obtained after running PTC-to-TDC.py" 1>&2
    echo 1>&2
    exit 1
fi

d="$1"
if [ ! -d "$d/filtered-medline" ] || [ ! -d "$d/pmc-abstracts"  ] || [ ! -d "$d/pmc-articles" ]; then
    echo "Error: one of the required subidrectories doesn't exist" 1>&2
    exit 1
fi

if [ -d "$d/unfiltered-medline" ] || [ -d "$d/abstracts+articles" ]; then
    echo "Error: at least one of the output dirs $d/unfiltered-medline or $d/abstracts+articles already exists" 1>&2
    exit 1
fi

mkdir "$d/unfiltered-medline"
pushd "$d/unfiltered-medline" >/dev/null
createLinks "filtered-medline" "MED"
createLinks "pmc-abstracts" "PMC"
popd >/dev/null

mkdir "$d/abstracts+articles"
pushd "$d/abstracts+articles" >/dev/null
createLinks "filtered-medline" "MED"
createLinks "pmc-articles" "PMC"
popd >/dev/null
