#!/bin/sh
for a in *ui; do pyuic4 -x $a -o `basename $a .ui`.py ; done
pyrcc4 icons.qrc -o icons_rc.py 
