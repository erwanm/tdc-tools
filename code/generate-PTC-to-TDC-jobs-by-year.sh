#!/bin/bash


script="/home/moreaue/brain-mend/pybioc/PTC-to-TDC.py"
yMax=2021

function writeJob {
    minYear="$1"
    maxYear="$2"
    sqsh="$3"
    targetDir="$4"

    echo '#!/bin/bash'
    echo
    echo "#SBATCH -p long"
    echo "#SBATCH -J $minYear"
    echo "#SBATCH -t 2-00:00:00"
    echo "ptcDir=\$(mktemp -d --tmpdir=/tmp \"ptc-to-tdc.XXXXXXXX\")"
    echo "squashfuse $sqsh \$ptcDir"
    echo "export PROOT_NO_SECCOMP=1"
    echo "/home/moreaue/udocker run -v ~ -v /tmp pybioc python3 $script \"\$ptcDir/BioCXML\" \"$targetDir\" $minYear $maxYear"
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


if [ $# -ne 4 ]; then
    echo "Usage: <PTC squashFS> <Y> <prefix job files> <target dir>" 1>&2
    echo "  Generates 1 job for all the years before Y then 1 job for every year." 1>&2
    exit 1
fi


sqsh=$(fullPathFile "$1")
yLimit="$2"
prefixjobs="$3"
targetDir="$4"

[ -d "$targetDir" ] || mkdir "$targetDir"
targetDir=$(fullPathDir "$targetDir")
writeJob 0 $yLimit "$sqsh" "$targetDir" >"$prefixjobs.0-$yLimit.sh"
for y in $(seq $yLimit $yMax); do
    writeJob $y $(( $y + 1 )) "$sqsh" "$targetDir" >"$prefixjobs.$y.sh"
done
writeJob $(( $yMax + 1 )) 3000 "$sqsh" "$targetDir" >"$prefixjobs.$yMax-3000.sh"
