#!/bin/bash

FPATH="$(dirname "$0")/FlameGraph/"
DROP_PERF_DATA=false
FPERF="$(pwd)/perf-output/"
PERF_SCRIPT_CMD="perf script"
PERF_REPORT=""
GREP_STRINGS=""
KERNEL_VERSION=""
MAXCPUNR=0
PER_CPU_FLAMEGRAPH=false
SUBTITLE=""
SYMFS=""
TAR=false
TITLE=""

# $1:$PSCRIPT $2:$TITLE $3:$SUBTITLE $4:$PSVG $5:$PFOLDED
__generate_flamegraph() {

	# extract the call stack for the flamegraph.pl to generate the svg interactive graph
	"${FPATH}"stackcollapse-perf.pl --all "$1" > "$5"

	if [[ $GREP_STRINGS == "" ]]; then
	    #cat ${PFOLDED} | ${FPATH}flamegraph.pl > ${PSVG}
	    grep -Pv 'addr2line|stackcollapse' "$5" | "${FPATH}"flamegraph.pl --color java --title "$2" --subtitle "$3" > "$4"
	else
	    # add the string name to the SVG name to identify the file easily
	    PSVG="$5S$GREP_STRINGS.svg"
	    grep -E "$GREP_STRINGS" "$5" | "${FPATH}"flamegraph.pl --color java --title "$2" --subtitle "$3" > "$4"
	fi

	if $DROP_PERF_DATA; then
		[ -e "$5" ] && rm "$5" # remove the $PFOLDED
		[ -e "$1" ] && rm "$1" # remove the $PSCRIPT

		if $TAR; then
			zip -u "${FPERF}$(basename "$PERF_REPORT")".zip "$4" # zip only the .svg
			[ -e "$4" ] && rm "$4" # remove the $PFOLDED
		fi
	else
		# If not keep only the .svg file, we need to zip all the intermediate files
		if $TAR; then
			zip -u "${FPERF}$(basename "$PERF_REPORT")".zip "$1" "$5" "$4"
		    # echo "# The perf-related file: \""${PSCRIPT}" "${PFOLDED}" "${PSVG}"\" has been tared."
		    rm "$1" "$5" "$4"
		    # echo "# Delete the related perf report files:" "${PSCRIPT}" "${PFOLDED}" "${PSVG}"
		fi
	fi

}

generate_per_cpu_flamegraph() {

	local CURRENT_LINE_NR=1
	local PREV_LINE_NR=1
	local CURRENT_CPU_NR=0
	local PREV_CPU_NR=0
	local FILE="$1"
	local PCPUSCRIPT
	local PCPUFOLDED
	local PCPUSVG
	# Associative array is local when it's declared inside the function
	declare -A cpu_array

	# $ grep -Pn '.+\s+\d+\s+\[\d+\] \d+\.\d+:\s+\d+\scycles:\s+' /var/log/easy-flamegraph/cpu/2020-02-11_220302.perf.cpu.t0.u12.1.script
	# 1:swapper     0 [000] 375287.542317:          1 cycles:
	# 26:swapper     0 [000] 375287.542324:          1 cycles:
	# 51:swapper     0 [000] 375287.542327:        178 cycles:

	while read -r i; do

		# Parse the current line number
		CURRENT_LINE_NR=$(echo "$i" |grep -Po '^\d+')

		if [ "$CURRENT_LINE_NR" = "" ]; then
			continue
		fi

		# echo LINE:$CURRENT_LINE_NR

		if [ "$CURRENT_LINE_NR" -ne "$PREV_LINE_NR" ]; then
			((CURRENT_LINE_NR = CURRENT_LINE_NR - 1))
			PCPUSCRIPT="${FPERF}$(basename "$PERF_REPORT").cpu${PREV_CPU_NR}.script"

			# Remove the previous script to avoid reuse the previous data
			if [ "${cpu_array[$PREV_CPU_NR]}"x == ""x ]; then
				# echo PREV_CPU_NR:$PREV_CPU_NR in if
				# echo cpu_array[PREV_CPU_NR]:${cpu_array[PREV_CPU_NR]} in if
				[ -e "$PCPUSCRIPT" ] && rm "$PCPUSCRIPT" && echo remove the existing "$PCPUSCRIPT"!
			fi

			#echo PREV_CPU_NR:$PREV_CPU_NR in else
			#echo cpu_array[PREV_CPU_NR]:$PREV_CPU_NR in else
			cpu_array[$PREV_CPU_NR]=$((${cpu_array[$PREV_CPU_NR]}+1))

			sed -n "$PREV_LINE_NR,${CURRENT_LINE_NR}p" "$FILE" >> "$PCPUSCRIPT"
			# echo "$PREV_LINE_NR,${CURRENT_LINE_NR}p $FILE >> ${PCPUSCRIPT}"
		fi

		PREV_LINE_NR=$CURRENT_LINE_NR

		# Parse the CPU number of the callstack
		PREV_CPU_NR=$(echo "$i" | perl -n -e '/\[(\d+)\]/; print $1')
		# echo CPU_NR:$PREV_CPU_NR

		if [ "$PREV_CPU_NR" -ge "$MAXCPUNR" ]; then
			MAXCPUNR="$PREV_CPU_NR"
		fi

	done <<< "$(grep -Pn '.+\s+\d+\s+\[\d+\] ' "$FILE")"

	# This is the case to handle the last callstack and try to get the last line
	CURRENT_LINE_NR=$(wc -l "$FILE" | awk '{print $1}')

	# echo $CURRENT_LINE_NR
	# Check the empty file condition that the while loop is skipped
	if [ "$PREV_LINE_NR" -lt "$CURRENT_LINE_NR" ] ; then
		PCPUSCRIPT="${FPERF}$(basename "$PERF_REPORT").cpu${PREV_CPU_NR}.script"

			# Remove the previous script to avoid reuse the previous data
			if [ "${cpu_array[$PREV_CPU_NR]}"x == ""x ]; then
				[ -e "$PCPUSCRIPT" ] && rm "$PCPUSCRIPT" && echo remove the existing "$PCPUSCRIPT"!
			fi

			cpu_array[$PREV_CPU_NR]=$((${cpu_array[$PREV_CPU_NR]}+1))

			sed -n "$PREV_LINE_NR,${CURRENT_LINE_NR}p" "$FILE" >> "$PCPUSCRIPT"
			# echo "$PREV_LINE_NR,${CURRENT_LINE_NR}p $FILE >> ${1}.cpu${PREV_CPU_NR}"
	fi

	# Remove leading 0
	MAXCPUNR=${MAXCPUNR#0}

	# Finally, generate the flamegraph
	for ((i = 0; i <= MAXCPUNR; i++)); do
		PCPUSCRIPT="${FPERF}$(basename "$PERF_REPORT")$(printf .cpu%03d "$i").script"
		PCPUFOLDED="${FPERF}$(basename "$PERF_REPORT")$(printf .cpu%03d "$i").folded"
		PCPUSVG="${FPERF}$(basename "$PERF_REPORT")$(printf .cpu%03d "$i").svg"

		__generate_flamegraph "$PCPUSCRIPT" "${TITLE}" "${SUBTITLE} - cpu $i" "${PCPUSVG}" "${PCPUFOLDED}"
	done

	# Use the following instructions to verify the correctness
	# $ grep -Pn '.+\s+\d+\s+\[\d+\] \d+\.\d+:\s+\d+\scycles:\s+' perf-output/perf.datacpu00*script | wc -l
	# 3968
	# $ grep -Pn '.+\s+\d+\s+\[\d+\] \d+\.\d+:\s+\d+\scycles:\s+' perf-output/perf.data.script | wc -l
	# 3968

}

generate_flamegraph() {

	if $PER_CPU_FLAMEGRAPH; then
		generate_per_cpu_flamegraph "${PSCRIPT}"
	fi

	# Always generate the *WHOLE* system flamegraph
	__generate_flamegraph "${PSCRIPT}" "${TITLE}" "${SUBTITLE}" "${PSVG}" "${PFOLDED}"

}

usage_function() {
            echo "usage: $0 -g <grep string to make specific flamegraph> -i <perf file> -k <kernel version #>"
            echo "	d - drop the perf related data(include perf.data!!) and keep the .svg flamegraph file to save space"
            echo "	g - grep strings - to grep specific strings e.g., kworker, to make flamegraph"
            echo "	i - perf report file"
            echo "	k - kernel version - specific kernel version number"
	    echo "	o - output directory - the output directory to save the .svg/script file"
            echo "	s - symfs - to assign the directory to search for the debug symbol of kernel modules"
            echo "	t - tar the $FPERF"
	    echo "	per-cpu-flamegraph - generate the flamegraph for each CPU"
	    echo "	subtitle - the subtitle of the framegraph"
	    echo "	title - the title of the framegraph"
}

clean_exit() {
	# nothing to do
	echo
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
		-p)
			PER_CPU_FLAMEGRAPH=$2
			shift 2
			;;
		--subtitle)
			SUBTITLE=$2
			shift 2
			;;
		--title)
			TITLE=$2
			shift 2
			;;
		"")
			shift
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
	if [ -e "$(pwd)/perf.data" ]; then
		PERF_REPORT="$(pwd)/perf.data"
        else
		echo "$(pwd)/perf.data doesn't exist!"
            echo "Please use -i to append the perf.data"
            exit 1
        fi
    else
	# assign the perf.data by '-i' but doesn't exist!
        echo "File doesn't exist: $PERF_REPORT!!"
	if [ -e "$(pwd)/perf.data" ]; then
		echo "Do you mean the $(pwd)/perf.data?"
        fi
        exit 1
    fi
fi

echo "Use the $PERF_REPORT as the source of the FlameGraph."

# check if the $PERF_REPORT is readable
if [ ! -r "$PERF_REPORT" ]; then
    echo "Permission denied: $PERF_REPORT cannot be read."
    echo "Try: \"sudo chmod a+r $PERF_REPORT\""
    exit 1
fi

# Try to clone the FlameGraph if it doesn't exist.
if [ -z "$(ls -A "$FPATH")" ]; then
    echo "Clone the FlameGraph by the following instructions:"

    echo "git submodule update --init FlameGraph"
    git submodule update --init FlameGraph
fi

PSCRIPT="${FPERF}$(basename "$PERF_REPORT").script"
PFOLDED="${FPERF}$(basename "$PERF_REPORT").folded"
PSVG="${FPERF}$(basename "$PERF_REPORT").svg"
PFOLDED_SUM="${FPERF}stack_sum"

# mkdir the folder to store the perf report data
mkdir -p "$FPERF"

# rm the zip file if it alreadys exists
if "$DROP_PERF_DATA"; then
	[ -e "${FPERF}$(basename "$PERF_REPORT")".zip ] && rm "${FPERF}$(basename "$PERF_REPORT")".zip && {
		echo "Remove the existing ${FPERF}$(basename "$PERF_REPORT").zip!"
	}
fi

# perf script -i ./perf-110417_201609 -k ~/ddebs/ddebs-4.4.0-53.74/usr/lib/debug/boot/vmlinux-4.4.0-53-generic > perf-110417_201609.perf
[[ $PERF_REPORT != "" ]] && PERF_SCRIPT_CMD="${PERF_SCRIPT_CMD} -i $PERF_REPORT"
[[ $KERNEL_VERSION != "" ]] && PERF_SCRIPT_CMD="${PERF_SCRIPT_CMD} -k $KERNEL_VERSION"
[[ $SYMFS != "" ]] && PERF_SCRIPT_CMD="${PERF_SCRIPT_CMD} --symfs $SYMFS"

#trap EXIT signal only
trap "clean_exit" EXIT

# generate the perf script file for the stackcollapse to extract the call stack
${PERF_SCRIPT_CMD} > "$PSCRIPT"

[ ! -s "$PSCRIPT" ] && echo "No perf data captured!"  && exit

generate_flamegraph

echo "###########"
if ! $TAR; then
	echo "# The whole system perf interactive .svg graph \"${PSVG}\" has been generated."
	if $PER_CPU_FLAMEGRAPH; then
		echo "# The per-cpu flamegraph : ${FPERF}$(basename "$PERF_REPORT").cpu[000-$(printf %03d "$MAXCPUNR")].svg"
	fi
	echo "#"
	echo "# The FlameGraph can be viewed by:"
	echo "# $ google-chrome-stable ${PSVG}"
	echo "# or"
	echo "# $ firefox ${PSVG}"
	echo "#"
else
	echo "# The intermediate files are in: ${FPERF}$(basename "$PERF_REPORT").zip"
	if $PER_CPU_FLAMEGRAPH; then
		echo "# The per-cpu flamegraph are also included: $(basename "$PERF_REPORT").cpu[000-$(printf %03d "$MAXCPUNR")].svg"
	fi
fi
echo "###########"
