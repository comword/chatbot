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

# try to extract translatable strings from .json files
echo "Extracting strings from json..."
if ! locales/extract_json_strings.py
then
    echo "Error in extract_json_strings.py. Aborting"
    cd $oldpwd
    exit 1
fi

# Update chatbot.pot
echo "Creating .pot file..."
pygettext3 -o locales/po/chatbot.pot *.py plugins/*.py locales/json/*.py
if [ $? -ne 0 ]; then
    echo "Error in pygettext3. Aborting"
    cd $oldpwd
    exit 1
fi

# Fix msgfmt errors
#if [ "`head -n1 locales/po/chatbot.pot`" = "# SOME DESCRIPTIVE TITLE." ]
#then
#    echo "Fixing .pot file headers..."
#    package="chatbot"
#    version=$(grep '^VERSION *= *' Makefile | tr -d [:space:] | cut -f 2 -d '=')
#    pot_file="locales/po/chatbot.pot"
#    sed -e "1,6d" \
#    -e "s/^\"Project-Id-Version:.*\"$/\"Project-Id-Version: $package $version\\\n\"/1" \
#    -e "/\"Plural-Forms:.*\"$/d" $pot_file > $pot_file.temp
#    mv $pot_file.temp $pot_file
#fi

# strip line-numbers from the .pot file
echo "Stripping .pot file from unneeded comments..."
if ! python locales/strip_line_numbers.py locales/po/chatbot.pot
then
    echo "Error in strip_line_numbers.py. Aborting"
    cd $oldpwd
    exit 1
fi

# Final compilation check
echo "Check pot-file compilation..."
if ! msgfmt -c -o /dev/null locales/po/chatbot.pot
then
    echo "Updated pot file contain gettext errors. Aborting."
    cd $oldpwd
    exit 1
fi

# Check for broken Unicode symbols
echo "Check for wrong Unicode symbols..."
if ! python locales/unicode_check.py locales/po/chatbot.pot
then
    echo "Updated pot file contain broken Unicode symbols. Aborting."
    cd $oldpwd
    exit 1
fi

echo "---"
echo "Update finished. It's safe to commit."
cd $oldpwd
