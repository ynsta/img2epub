#!/usr/bin/false

unset IFS

function getoptions_help() {
    IFS=':';
    for o in "${GETOPTIONS[@]}"; do
	OPTION=($o)
	echo -n "  --${OPTION[0]}"
	if [ ${OPTION[1]} = 1 ]; then
	    echo -n "=ARG "
	    echo -n ${OPTION[2]}
	    DEFAULT=$(eval echo \$GOPT__$(echo ${OPTION[0]} | tr 'a-z' 'A-Z'))
	    echo " (${DEFAULT})"
	else
	    echo -n "     "
	    echo ${OPTION[2]}
	fi
    done
    unset IFS
}

function in_options() {
    have_arg=$1
    test_opt=$2

    IFS=':'
    for o in "${GETOPTIONS[@]}"; do
	OPTION=($o)
	if [ "${test_opt}" = "${OPTION[0]}" ]; then
	    if [ "${OPTION[1]}" != "${have_arg}" ]; then
		return 1
	    else
		return 0
	    fi
	fi
	unset OPTION
    done
    unset IFS
    return 1
}

GOPT_ARGC=0
for ARGV; do
    case "$ARGV" in
	--*=*)
	    VAR=${ARGV%%=*}
	    VAR=${VAR#--}
	    ARG=${ARGV#--*=}
	    if in_options 1 "$VAR"; then
		VAR=$(echo ${VAR} | tr 'a-z' 'A-Z')
		eval "export GOPT__${VAR}=\"${ARG}\""
	    else
		GOPT_ERROR=1
		GOPT_ERROR_STR=$ARGV
		break
	    fi
	    ;;

	--*)
	    VAR=${ARGV#--}
	    if in_options 0 "$VAR"; then
		VAR=$(echo $VAR | tr 'a-z' 'A-Z')
		eval "export GOPT__${VAR}=1"
	    else
		GOPT_ERROR=1
		GOPT_ERROR_STR=$ARGV
		break
	    fi
	    ;;

	*)
	    tmp_argv[$GOPT_ARGC]=${ARGV}
	    GOPT_ARGC=$((GOPT_ARGC + 1))
	    ;;
    esac
done

GOPT_IFS=':'
IFS=$GOPT_IFS
GOPT_ARGV="${tmp_argv[@]}"
unset IFS
unset tmp_argv

export GOPT_ARGV
export GOPT_ARGC
export GOPT_IFS
