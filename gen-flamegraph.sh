#!/bin/bash

FPATH="$(dirname "$0")/FlameGraph/"
DROP_PERF_DATA=false
FPERF="$(pwd)/perf-output/"
TRACE_SRC="perf"
PERF_SCRIPT_CMD="perf script"
PERF_REPORT=""
GREP_STRINGS=""
HEADER_INFO=true
PCRE_STRING=""
KERNEL_VERSION=""
MAXCPUNR=0
MEM_FLAME=false
PER_CPU_FLAMEGRAPH=false
PSVG=""
PFOLDED=""
SUBTITLE=""
SYMFS=""
TAR=false
TITLE=""

usage_function() {
            echo "usage: $0 -g <grep string to make specific flamegraph> -i <perf file> -k <kernel version #>"
            echo "	-d - drop the intermediate perf related data(include script/folded!!) and keep the .svg flamegraph file to save space"
            echo "	-g - grep strings - to grep specific strings e.g., kworker, to make flamegraph"
            echo "	-i - perf report file"
            echo "	-k - kernel version - specific kernel version number"
	    echo "	-o - output directory - the output directory to save the .svg/script file"
            echo "	-s - symfs - to assign the directory to search for the debug symbol of kernel modules"
            echo "	-t - tar the $FPERF"
	    echo "	-p [true|false] -  generate the flamegraph for each CPU"
	    echo "	-I [true|false] - default:[false], the flag will disable printing the info from perf header"
	    echo "	--ftrace - indicate that the input data is from ftrace/trace-cmd"
	    echo "	--mem-flame - generate the flamegraph based on the byte(ftrace/trace-cmd only)"
	    echo "	--pcre - use the Perl Compatible Regular Expression"
	    echo "	--subtitle - the subtitle of the flamegraph"
	    echo "	--title - the title of the framegraph"
}

# $1:options $2:strings $3:error messages
empty_check() {
		if [ "$2" == "" ]; then
			echo "$3"
			usage_function
			exit 1
		fi

		# check if the option which needs argument followed with another option
		# ex: $ ./gen-flamegraph.sh -k --ftrace
		# fatal: option -k must come before non-option arguments
		[[ $2 =~ ^- ]] && echo "fatal: option $1 must come before non-option arguments" && exit 1
}

perf_examination() {
	# check if the command line has assign the perf.data file. e.g. '-i xxx.perf.data'
	if [ ! -e "$PERF_REPORT" ]; then
		if [ -z "$PERF_REPORT" ]; then
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
}

ftrace_examination() {
	if [ ! -e "$PERF_REPORT" ]; then
		if [ -z "$PERF_REPORT" ]; then
			echo "Please use -i to append the ftrace log"
		else
			# assign the perf.data by '-i' but doesn't exist!
			echo "File doesn't exist: $PERF_REPORT!!"
		fi
		exit 1
	fi
}

tracing_source_examination() {
	# Check the file existence and try to guess the possible name if the file name
	# is not given.
	case "$TRACE_SRC" in
		perf)
			perf_examination
			;;
		ftrace)
			if $PER_CPU_FLAMEGRAPH; then
				echo "${FUNCNAME[0]}: The per-cpu flamegraph for ftrace is not implemented!!"
				#exit 1
			fi
			ftrace_examination
			;;
		*)
			echo "${FUNCNAME[0]}: Invalid tracing source: $TRACE_SRC!!"
			exit 1
			;;
	esac
}

tracing_data_permission_check() {
	echo "[$TRACE_SRC] Use the $PERF_REPORT as the source of the FlameGraph."

	# check if the $PERF_REPORT is readable
	if [ ! -r "$PERF_REPORT" ]; then
		echo "Permission denied: $PERF_REPORT cannot be read."
		echo "Try: \"sudo chmod a+r $PERF_REPORT\""
		exit 1
	fi
}

flamegraph_init() {
	# Try to clone the FlameGraph if it doesn't exist.
	if [ -z "$(ls -A "$FPATH")" ]; then
		echo "Clone the FlameGraph by the following instructions:"

		echo "git submodule update --init FlameGraph"
		git submodule update --init FlameGraph
	fi
}

# $1:$PSCRIPT $2:$TITLE $3:$SUBTITLE $4:$PSVG $5:$PFOLDED
__generate_flamegraph() {
	local SVG
	local SUBTITLE="$3"
	local TRACE_CMD_OTIONS="--process_name"
	local COUNT_NAME=""

	case "$TRACE_SRC" in
		perf)
			# extract the call stack for the flamegraph.pl to generate the svg interactive graph
			"${FPATH}"stackcollapse-perf.pl --all "$1" > "$5"
			;;
		ftrace)
			# extract the call stack for the flamegraph.pl to generate the svg interactive graph
			if $MEM_FLAME; then
				TRACE_CMD_OTIONS="$TRACE_CMD_OTIONS --page_type --page_order"
				COUNT_NAME="--countname KB"
			fi

			"${FPATH}"stackcollapse-tracecmd.pl $TRACE_CMD_OTIONS "$1" > "$5"
			# TODO: The header info of ftrace still need to be implemented
			if [ $? -ne 0 ]; then
				echo "${FUNCNAME[0]}: Invalid command \"${FPATH}stackcollapse-tracecmd.pl --all $1 > $5"\"
				exit 1
			fi
			;;
		*)
			echo "${FUNCNAME[0]}: Invalid tracing source: $TRACE_SRC!!"
			exit 1
			;;
	esac

	# grep the required string
	if [[ "$GREP_STRINGS" == "" && "$PCRE_STRING" == "" ]]; then
		#cat ${PFOLDED} | ${FPATH}flamegraph.pl > ${PSVG}
		grep -Pv 'addr2line|stackcollapse' "$5" | "${FPATH}"flamegraph.pl --color java --title "$2" --subtitle "$SUBTITLE" $COUNT_NAME > "$4"
	elif [[ "$PCRE_STRING" != "" ]]; then
		# add the string name to the SVG name to identify the file easily
		SVG="${5%.folded}.pcre.svg"
		SUBTITLE="$SUBTITLE pcre:\"$PCRE_STRING\""
		grep -P "$PCRE_STRING" "$5" | "${FPATH}"flamegraph.pl --color java --title "$2" --subtitle "$SUBTITLE" $COUNT_NAME > "$SVG"
	else
		# add the string name to the SVG name to identify the file easily
		SVG="${5%.folded}.S$GREP_STRINGS.svg"
		SUBTITLE="$SUBTITLE grep:\"$GREP_STRINGS\""
		grep -E "$GREP_STRINGS" "$5" | "${FPATH}"flamegraph.pl --color java --title "$2" --subtitle "$SUBTITLE" $COUNT_NAME > "$SVG"
	fi

	# drop the intermediate data
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

generate_flamegraph_perf() {
	local HEADER

	PSCRIPT="${FPERF}$(basename "$PERF_REPORT").script"

	# perf script -i ./perf-110417_201609 -k ~/ddebs/ddebs-4.4.0-53.74/usr/lib/debug/boot/vmlinux-4.4.0-53-generic > perf-110417_201609.perf
	[[ $PERF_REPORT != "" ]] && PERF_SCRIPT_CMD="${PERF_SCRIPT_CMD} -i $PERF_REPORT"
	[[ $KERNEL_VERSION != "" ]] && PERF_SCRIPT_CMD="${PERF_SCRIPT_CMD} -k $KERNEL_VERSION"
	[[ $SYMFS != "" ]] && PERF_SCRIPT_CMD="${PERF_SCRIPT_CMD} --symfs $SYMFS"

	# To get the number of the cpu, we cannot use $(getconf _NPROCESSORS_ONLN), as
	# the perf.data report will be generated remotely.
	NRPROCESSORS=$(perf report --header -i $PERF_REPORT | grep nrcpus | perl -n -e '/nrcpus\s+avail\s+\:\s+(\d+)/; print $1')
	MAXCPUNR=$((NRPROCESSORS-1))

	# grep the useful header info and add to subtitle
	# HEADER=$(perf report --header -I -i $PERF_REPORT| grep -P "nrcpus|captured|os release|hostname|total memory|cmdline|node\d+")
	if $HEADER_INFO; then
		HEADER=$(perf report --header -I -i $PERF_REPORT| grep -P "captured|os release|hostname|node\d+")
		SUBTITLE="${SUBTITLE}${HEADER}"
	fi

	if $PER_CPU_FLAMEGRAPH; then
		echo -n "Generating per-cpu flamegraph"
		for i in $(seq 0 $((MAXCPUNR))); do
			# generating flamegraph for each cpu will generate a dot to show the status.
			echo -n "."
			# The ${PERF_SCRIPT_CMD} cannot be double quoted as it's executing command
			${PERF_SCRIPT_CMD} -C "$i" > "${FPERF}""$(basename "$PERF_REPORT")$(printf .cpu%03d "$i")".script
			PCPUSCRIPT="${FPERF}$(basename "$PERF_REPORT")$(printf .cpu%03d "$i").script"
			PCPUFOLDED="${FPERF}$(basename "$PERF_REPORT")$(printf .cpu%03d "$i").folded"
			PCPUSVG="${FPERF}$(basename "$PERF_REPORT")$(printf .cpu%03d "$i").svg"

			__generate_flamegraph "$PCPUSCRIPT" "${TITLE}" "${SUBTITLE} - cpu $i" "${PCPUSVG}" "${PCPUFOLDED}"
		done
		# new line
		echo
	fi

	# generate the perf script file for the stackcollapse to extract the call stack
	${PERF_SCRIPT_CMD} > "$PSCRIPT"

	[ ! -s "$PSCRIPT" ] && echo "No perf data captured!"  && exit

	# Always generate the *WHOLE* system flamegraph
	__generate_flamegraph "${PSCRIPT}" "${TITLE}" "${SUBTITLE}" "${PSVG}" "${PFOLDED}"
}

generate_flamegraph_ftrace() {
	# Always generate the *WHOLE* system flamegraph
	PSCRIPT="$PERF_REPORT"
	__generate_flamegraph "${PSCRIPT}" "${TITLE}" "${SUBTITLE}" "${PSVG}" "${PFOLDED}"
}

clean_exit() {
	# nothing to do
	:
}

generate_flamegraph() {
	# mkdir the folder to store the perf report data
	mkdir -p "$FPERF"

	#trap EXIT signal only
	trap "clean_exit" EXIT

	# rm the zip file if it already exists
	if "$DROP_PERF_DATA"; then
		[ -e "${FPERF}$(basename "$PERF_REPORT")".zip ] && rm "${FPERF}$(basename "$PERF_REPORT")".zip && {
			echo "Remove the existing ${FPERF}$(basename "$PERF_REPORT").zip!"
		}
	fi

	PFOLDED="${FPERF}$(basename "$PERF_REPORT").folded"
	PSVG="${FPERF}$(basename "$PERF_REPORT").svg"
	PFOLDED_SUM="${FPERF}stack_sum"

	case "$TRACE_SRC" in
		perf)
			generate_flamegraph_perf
			;;
		ftrace)
			generate_flamegraph_ftrace
			;;
		*)
			echo "${FUNCNAME[0]}: Invalid tracing source: $TRACE_SRC!!"
			exit 1
			;;
	esac
}

output_messages() {
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
			empty_check "-g" "$GREP_STRINGS" "The -g <grep string> is empty!!"
			shift 2
			;;
		-i)
			PERF_REPORT=$2
			empty_check "-i" "$PERF_REPORT" "The -i <input file> is empty!!"
			shift 2
			;;
		-k)
			KERNEL_VERSION=$2
			empty_check "-k" "$KERNEL_VERSION" "The -k <kernel version> is empty!!"
			shift 2
			;;
		-o)
			FPERF=$2/
			empty_check "-o" "$FPERF" "The -o <output directory> is empty!!"
			shift 2
			;;
		-s)
			SYMFS=$2
			empty_check "$SYMFS" "The -s <symbolic directory> is empty!!"
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
		--ftrace)
			TRACE_SRC="ftrace"
			shift
			;;
		--mem-flame)
			MEM_FLAME=true
			shift
			;;
		--pcre)
			PCRE_STRING="$2"
			empty_check "--pcre" "$PCRE_STRING" "The --pcre <grep string> is empty!!"
			shift 2
			;;
		-p|--per-cpu)
			if [[ $2 == "true" || $2 == "false" ]]; then
				PER_CPU_FLAMEGRAPH=$2
				shift 2
			else
				PER_CPU_FLAMEGRAPH=true
				shift 1
			fi
			;;
		-I)
			if [[ $2 == "true" || $2 == "false" ]]; then
				HEADER_INFO=$2
				shift 2
			else
				# By default, the header is enabled. So, let the default option to disable the header info.
				HEADER_INFO=false
				shift 1
			fi
			;;
		--subtitle)
			SUBTITLE=$2
			empty_check "--subtitle" "$SUBTITLE" "The --subtitle <subtitle description> is empty!!"
			shift 2
			;;
		--title)
			TITLE=$2
			empty_check "--title" "$TITLE" "The --title <title description> is empty!!"
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

tracing_source_examination

tracing_data_permission_check

flamegraph_init

generate_flamegraph

output_messages
