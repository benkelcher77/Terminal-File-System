#!/bin/sh

TEMPFILE="$(mktemp -t "tmp.XXXXXXXX")"
fm.py ${TEMPFILE}
cd $(cat ${TEMPFILE})
rm -f ${TEMPFILE}
