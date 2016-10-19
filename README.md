# xmppbot
This is a extendable bot with xmpp protocol.

# install
pip3 install PyYAML
pip3 install sleekxmpp
pip3 install plyvel
pip3 install babel

# make translation
pygettext3 -o xmppbot.pot -p locales *.py
pygettext3 -o xmppbot.pot -p locales plugins/*.py
msginit -l zh_CN -o locales/po/zh_CN.po -i locales/xmppbot.pot
mkdir -p locales/mo/zh_CN/LC_MESSAGES/
msgfmt -D locales/po -c -v -o locales/mo/zh_CN/LC_MESSAGES/xmppbot.mo zh_CN.po
