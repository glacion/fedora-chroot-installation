#!/bin/sh

ESP=/boot # Change if your EFI System Partition is on a different partition.
TARGET_PATH=$ESP/EFI/fedora # Feel free to change this, as long as it is in the ESP.

PKG=$(rpm -q kernel | tail -n 1)
PKG_VER=$(echo $PKG | sed 's/kernel-//g')
MACHINE_ID=$(cat /etc/machine-id)
SOURCE_PATH=$ESP/$MACHINE_ID/$PKG_VER

if [ ! -d $TARGET_PATH ]; then
    mkdir -p $TARGET_PATH
fi

cp -f $SOURCE_PATH/linux $TARGET_PATH/
cp -f $SOURCE_PATH/initrd $TARGET_PATH/
