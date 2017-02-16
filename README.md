# xmppbot

This is a extendable bot with xmpp protocol.

# install

apt-get install gettext build-essential libleveldb-dev libpython3-dev

pip3 install PyYAML

pip3 install sleekxmpp

pip3 install plyvel

pip3 install flask

mkdir -p datas

## For module to suppout IRC protocol

pip3 install irc3

## For module to suppout telegram protocol

pip3 install python-telegram-bot --upgrade

# update pot file

locales/generate_pot.sh

# make translation

msginit -l zh_CN -o locales/po/zh_CN.po -i locales/po/xmppbot.pot

locales/compile_mo.sh
