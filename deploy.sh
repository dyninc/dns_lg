#!/usr/bin/env bash

#/bin/sh
set -e

if [ "$EUID" -ne "0" ] ; then
  echo "Script must be run as root." >&2
  exit 1
fi

if which puppet -e /dev/null ; then
  echo "Puppet must be installed."
  exit 1
fi

cd `dirname $0`
puppet apply puppet/setup.pp

