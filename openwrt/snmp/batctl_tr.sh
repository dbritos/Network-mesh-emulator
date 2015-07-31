#!/bin/sh
if test "$1" = '-s' ;
        then
                  
		BAT=$(batctl tr $4 | sed -n 's/.*\(..:..:..:..:..:..\)[ ,\*]\+\([0-9][0-9]*\.[0-9][0-9]*\).*/\2 \1/p')
                echo $BAT > trace
                exit
elif test "$1" = '-g' ;
        then
               BAT=$(cat trace)
               echo $2
               echo "string"
               echo $BAT
fi


