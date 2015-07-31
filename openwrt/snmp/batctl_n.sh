#!/bin/sh
if test "$1" = '-s' ;
	then
		exit
elif test "$1" = '-g' ;
	then
	       BAT=$(batctl o | sed -n 's/^\(..:..:..:..:..:..\).* \(..:..:..:..:..:..\).*/\1 \2/p')
               echo $2
               echo "string"
               echo $BAT
fi

