#!/usr/bin/env bash

oldpwd=`pwd`

if [ ! -d locales/po ]
then
    if [ -d ../locales/po ]
    then
        cd ..
    else
        echo "Error: Could not find locales/po subdirectory."
        exit 1
    fi
fi

# merge incoming translations for each language specified on the commandline
if [ $# -gt 0 ]
then
    for n in $@
    do
        if [ -f locales/incoming/${n}.po ]
        then
            if [ -f locales/po/${n}.po ]
            then
                echo "merging locales/incoming/${n}.po"
                msgcat -F --use-first locales/incoming/${n}.po locales/po/${n}.po -o locales/po/${n}.po && rm locales/incoming/${n}.po
            else
                echo "importing locales/incoming/${n}.po"
                mv locales/incoming/${n}.po locales/po/${n}.po
            fi
        fi
    done
# if nothing specified, merge all incoming translations
elif [ -d locales/incoming ]
then
    shopt -s nullglob # work as expected if nothing matches *.po
    for f in locales/incoming/*.po
    do
        n=`basename ${f} .po`
        if [ -f locales/po/${n}.po ]
        then
            echo "merging ${f}"
            msgcat -F --use-first ${f} locales/po/${n}.po -o locales/po/${n}.po && rm ${f}
        else
            echo "importing ${f}"
            mv ${f} locales/po/${n}.po
        fi
    done
fi

# merge locales/po/chatbot.pot with .po file for each specified language
if [ $# -gt 0 ]
then
    for n in $@
    do
        echo "updating locales/po/${n}.po"
        msgmerge -F -U locales/po/${n}.po locales/po/chatbot.pot
    done
# otherwise merge locales/po/chatbot.pot with all .po files in locales/po
else
    for f in locales/po/*.po
    do
        echo "updating $f"
        msgmerge -F -U $f locales/po/chatbot.pot
    done
fi

cd $oldpwd
