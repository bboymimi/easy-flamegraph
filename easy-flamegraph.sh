#!/bin/bash

FPATH="`dirname $0`/FlameGraph/"
DROP_PERF_DATA=false
FPERF="`pwd`/perf-output/"
PERF_SCRIPT_CMD="perf script"
PERF_REPORT=""
GREP_STRINGS=""
KERNEL_VERSION=""
SYMFS=""
TAR=false
#DATE=$(date +%Y-%m-%d_%H:%M:%S)
DATE=""

usage_function() {
            echo "usage: $0 -g <grep string to make specific flamegraph> -i <perf file> -k <kernel version #>"
            echo "	d - drop the perf related data(include perf.data!!) and keep the .svg flamegraph file to save space"
            echo "	g - grep strings - to grep specific strings e.g., kworker, to make flamegraph"
            echo "	i - perf report file"
            echo "	k - kernel version - specific kernel version number"
	    echo "	o - output directory - the output directory to save the .svg/script file"
            echo "	s - symfs - to assign the directory to search for the debug symbol of kernel modules"
            echo "	t - tar the $FPERF"
}

clean_exit() {

	if $DROP_PERF_DATA; then
		[ -e "${PFOLDED}" ] && rm "${PFOLDED}"
		[ -e "${PSCRIPT}" ] && rm "${PSCRIPT}"
	fi

}

while (($# > 0))
do
	case $1 in
		-d)
			DROP_PERF_DATA=true
			shift
			;;
		-g)
			GREP_STRINGS=$2
			shift 2
			;;
		-i)
			PERF_REPORT=$2
			shift 2
			;;
		-k)
			KERNEL_VERSION=$2
			shift 2
			;;
		-o)
			FPERF=$2/
			shift 2
			;;
		-s)
			SYMFS=$2
			shift 2
			;;
		-t)
			TAR=true
			shift
			;;
		-h|--help)
			usage_function
			exit 0
			;;
		*)
			echo "Error!! Invalid input: $1"
			usage_function
			exit 1
			;;
	esac
done

# check if the command line has assign the perf.data file. e.g. '-i xxx.perf.data'
if [ ! -e "$PERF_REPORT" ]; then
    if [ x"$PERF_REPORT" = x"" ]; then
        # if command didn't assign the perf data, go ahead to check the current folder
        if [ -e "`pwd`/perf.data" ]; then
	    PERF_REPORT="`pwd`/perf.data"
        else
            echo "`pwd`/perf.data doesn't exist!"
            echo "Please use -i to append the perf.data"
            exit -1
        fi
    else
	# assign the perf.data by '-i' but doesn't exist!
        echo "File doesn't exist: $PERF_REPORT!!"
        if [ -e "`pwd`/perf.data" ]; then
            echo "Do you mean the `pwd`/perf.data?"
        fi
        exit -1
    fi
fi

echo "Use the $PERF_REPORT as the source of the FlameGraph."

# check if the $PERF_REPORT is readable
if [ ! -r $PERF_REPORT ]; then
    echo "Permission denied: $PERF_REPORT cannot be read."
    echo "Try: \"sudo chmod a+r $PERF_REPORT\""
    exit -1
fi

# Try to clone the FlameGraph if it doesn't exist.
if [ -z "$(ls -A "$FPATH")" ]; then
    echo "Clone the FlameGraph by the following instructions:"

    echo "git submodule update --init FlameGraph"
    git submodule update --init FlameGraph
fi

PSCRIPT="${FPERF}`basename ${PERF_REPORT}`.script"
PFOLDED="${FPERF}`basename ${PERF_REPORT}`.folded"
PSVG="${FPERF}`basename ${PERF_REPORT}`.svg"
PFOLDED_SUM="${FPERF}stack_sum"

# mkdir the folder to store the perf report data
mkdir -p ${FPERF}

# perf script -i ./perf-110417_201609 -k ~/ddebs/ddebs-4.4.0-53.74/usr/lib/debug/boot/vmlinux-4.4.0-53-generic > perf-110417_201609.perf
[[ $PERF_REPORT != "" ]] && PERF_SCRIPT_CMD="${PERF_SCRIPT_CMD} -i $PERF_REPORT"
[[ $KERNEL_VERSION != "" ]] && PERF_SCRIPT_CMD="${PERF_SCRIPT_CMD} -k $KERNEL_VERSION"
[[ $SYMFS != "" ]] && PERF_SCRIPT_CMD="${PERF_SCRIPT_CMD} --symfs $SYMFS"

#trap EXIT signal only
trap "clean_exit" EXIT

# generate the perf script file for the stackcollapse to extract the call stack
${PERF_SCRIPT_CMD} > ${PSCRIPT}

[ ! -s ${PSCRIPT} ] && echo "No perf data captured!"  && exit

# extract the call stack for the flamegraph.pl to generate the svg interactive graph
${FPATH}stackcollapse-perf.pl --all ${PSCRIPT} > ${PFOLDED}

# cat all the callgraph to make the summary
cat ${PFOLDED} >> ${PFOLDED_SUM}

if [[ $GREP_STRINGS == "" ]]; then
    #cat ${PFOLDED} | ${FPATH}flamegraph.pl > ${PSVG}
    grep -Pv 'addr2line|stackcollapse' ${PFOLDED} | ${FPATH}flamegraph.pl --color java > ${PSVG}
else
    # add the string name to the SVG name to identify the file easily
    PSVG="${PFOLDED}S$GREP_STRINGS.svg"
    egrep $GREP_STRINGS ${PFOLDED} | ${FPATH}flamegraph.pl > ${PSVG}
fi

if $TAR; then
    tar zcvf "${FPERF}""${PERF_REPORT}".tar.gz "${PSCRIPT}" "${PFOLDED}" "${PSVG}"
    # echo "# The perf-related file: \""${PSCRIPT}" "${PFOLDED}" "${PSVG}"\" has been tared."
    rm "${PSCRIPT}" "${PFOLDED}" "${PSVG}"
    # echo "# Delete the related perf report files:" "${PSCRIPT}" "${PFOLDED}" "${PSVG}"
fi

echo "###########"
echo "# The perf interactive .svg graph \"${PSVG}\" has been generated."
echo "#"
echo "# The FlameGraph can be viewed by:"
echo "# $ google-chrome-stable ${PSVG}"
echo "# or"
echo "# $ firefox ${PSVG}"
echo "#"
if $TAR; then
	echo "# The intermediate files are in: "${FPERF}""${PERF_REPORT}".tar.gz"
fi
echo "###########"
