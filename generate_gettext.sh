#!/bin/sh
xgettext -k_ --copyright-holder="Zeray Rice" --package-name=stormwind --package-version=`cat VERSION` --msgid-bugs-address="fanzeyi1994@gmail.com" --language=Python `find . -name "*.py" -or -name "*.html" | grep "^./venv" --color=never -v` -o i18n/message.po
