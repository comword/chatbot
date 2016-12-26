# xmppbot

This is a extendable bot with xmpp protocol.

# install

pip3 install PyYAML

pip3 install sleekxmpp

pip3 install plyvel

# make translation

pygettext3 -o xmppbot.pot -p locales *.py plugins/*.py

msginit -l en_US -o locales/po/en_US.po -i locales/xmppbot.pot

mkdir -p locales/mo/en_US/LC_MESSAGES/

msgfmt -D locales/po -c -v -o locales/mo/en_US/LC_MESSAGES/xmppbot.mo en_US.po

msginit -l zh_CN -o locales/po/zh_CN.po -i locales/xmppbot.pot

mkdir -p locales/mo/zh_CN/LC_MESSAGES/

msgfmt -D locales/po -c -v -o locales/mo/zh_CN/LC_MESSAGES/xmppbot.mo zh_CN.po
