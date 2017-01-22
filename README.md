# xmppbot

This is a extendable bot with xmpp protocol.

# install

pip3 install PyYAML

pip3 install sleekxmpp

pip3 install plyvel

# update pot file

locales/generate_pot.sh

# make translation

msginit -l zh_CN -o locales/po/zh_CN.po -i locales/po/xmppbot.pot

locales/compile_mo.sh
