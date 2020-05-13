#!/bin/bash
#
# MIT licensed, see ./LICENSE
#
# Copyright (c) 2020 Holger Levsen
#
set -e

#
# define paths
#
DEPLOYMENT_TMPDIR="$(dirname $0)/deploy"
mkdir -p $DEPLOYMENT_TMPDIR
SOURCE="$(dirname $0)/esp32/boot.py"
TARGET=$DEPLOYMENT_TMPDIR/boot.py

#
# load custom config
#
CONFIG="$(dirname $0)/config"
if [ ! -f $CONFIG ] ; then
	echo "$CONFIG does not exist, please create it by copying from $CONFIG.example"
	exit 1
elif [ ! -x $CONFIG ] ; then
	echo "$CONFIG exists, but is not executable."
	exit 1
fi
source $CONFIG

#
# this script uses ampy for deployment to the esp32
#
if ! which ampy 1>&2 > /dev/null ; then
	echo "Cannot find ampy in path, exiting."
	echo "Please install ampy from https://github.com/pycampers/ampy"
	exit 1
fi

#
# some help text
#
echo "Thank you for running $0."
echo
echo "According to $CONFIG the esp32 is connected to $USBDEVICE"
echo
echo "Further you need to attach to the serial console of the esp32, eg using"
echo "'minicom -D $USBDEVICE' as you will need to press CTRL-somekey there:"
echo

#
# main loop, handy for development
#
while true ; do
	echo "-----------------------------------------------------------------"
	echo
	echo "First, you need to interrupt the program on the esp32 by pressing"
	echo "CTRL-C there. Second, press CTRL-A there to switch the esp32 in the"
	echo "right mode for receiving the programm."
	echo

	echo "Third press ENTER here to deploy $SOURCE to the esp32 connected"
	echo "via $USBDEVICE:"
	read a

	#
	# prepare deployment
	#
	echo "Modifying $SOURCE using variables from $CONFIG."
	cp $SOURCE $TARGET
	sed -i "s#SSID#$SSID#" $TARGET
	sed -i "s#PASSWORD#$PASSWORD#" $TARGET
	sed -i "s#NTPHOST#$NTPHOST#" $TARGET

	#
	# deploy
	#
	echo "Deploying $TARGET to $USBDEVICE."
	sudo ampy -p $USBDEVICE put $TARGET || exit 1
	echo "Done."
	echo
	echo "Fourth and finally press CTRL-D on the esp32 to reboot it."
	sleep 10
	echo
	echo "Looping forever... press CTRL-C here to interrupt $0."
	echo
done
