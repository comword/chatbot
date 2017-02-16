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

if [ -z $LOCALE_DIR ]
then
    LOCALE_DIR="locales/mo"
fi

if [ $# -gt 0 ] && [ $1 != "all" ]
then
    for n in $@
    do
        f="locales/po/${n}.po"
        mkdir -p $LOCALE_DIR/${n}/LC_MESSAGES
        msgfmt -c -v -f -o $LOCALE_DIR/${n}/LC_MESSAGES/chatbot.mo ${f}
    done
else
# if nothing specified, compile .mo file for every .po file in locales/po
    for f in locales/po/*.po
    do
        n=`basename $f .po`
        mkdir -p $LOCALE_DIR/${n}/LC_MESSAGES
        msgfmt -c -v -f -o $LOCALE_DIR/${n}/LC_MESSAGES/chatbot.mo ${f}
    done
fi

cd $oldpwd
