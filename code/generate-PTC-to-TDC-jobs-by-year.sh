#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"
yMax=2021

function writeJob {
    minYear="$1"
    maxYear="$2"
    sqsh="$3"
    targetDir="$4"
    clusterPart="$5"

    echo '#!/bin/bash'
    echo
    echo "#SBATCH -p $clusterPart"
    echo "#SBATCH -J $minYear"
#    echo "#SBATCH -t 2-00:00:00"
#    echo "SBATCH --mem=30G"
    echo "ptcDir=\$(mktemp -d --tmpdir=/tmp \"ptc-to-tdc.XXXXXXXX\")"
    echo "squashfuse $sqsh \$ptcDir"
    echo "export PROOT_NO_SECCOMP=1"
    echo "/home/moreaue/udocker run -v ~ -v /tmp pybioc python3 $DIR/PTC-to-TDC.py \"\$ptcDir/BioCXML\" \"$targetDir\" $minYear $maxYear >$minYear-$maxYear.out 2>$minYear-$maxYear.err"
    echo "fusermount -u \$ptcDir"
    echo "rmdir \$ptcDir"    
}


function fullPathFile {
    f="$1"
    pushd $(dirname "$f") >/dev/null
    echo $(pwd)/$(basename "$f")
    popd >/dev/null
}

function fullPathDir {
    d="$1"
    pushd "$d" >/dev/null
    pwd
    popd >/dev/null
}


if [ $# -ne 5 ]; then
    echo "Usage: <PTC squashFS> <Y> <prefix job files> <target dir> <cluster part>" 1>&2
    echo "  Generates 1 job for all the years before Y then 1 job for every year." 1>&2
    exit 1
fi


sqsh=$(fullPathFile "$1")
yLimit="$2"
prefixjobs="$3"
targetDir="$4"
clusterPart="$5"

[ -d "$targetDir" ] || mkdir "$targetDir"
targetDir=$(fullPathDir "$targetDir")
writeJob 0 $yLimit "$sqsh" "$targetDir" "$clusterPart" >"$prefixjobs.0-$yLimit.sh"
for y in $(seq $yLimit $yMax); do
    writeJob $y $(( $y + 1 )) "$sqsh" "$targetDir" "$clusterPart" >"$prefixjobs.$y.sh"
done
writeJob $(( $yMax + 1 )) 3000 "$sqsh" "$targetDir" "$clusterPart" >"$prefixjobs.$yMax-3000.sh"
