#!/usr/bin/env python3

from subprocess import check_output, CalledProcessError
from shutil import copy2
from os import makedirs, path, geteuid
from sys import argv, exit
from typing import Tuple, List, Optional

Command = Tuple[str, ...]


def read_cmd(cmd: Command) -> str:
    """Reads the output of a command and decodes into utf8 string.

    Args:
        cmd: Command to run.
    Returns:
        utf8 Encoded string from the output of the called subprocess.
    """
    return check_output(cmd).decode('utf-8')


def read_cmd_list(cmd: Command) -> List[str]:
    """Creates a list of utf8 strings from the output of given command
    seperated by newline.

    Args:
        cmd: Command to run.
    Returns:
        List of utf8 strings from the output of given command
        seperated by newline.
    """
    return read_cmd(cmd).splitlines()


def find_esp() -> Optional[str]:
    """Locates the EFI System Partition's mountpoint.
       NOTE: It can only determine if the ESP is in /boot/efi or /boot.
       If your ESP is mounted in another location, you must run this script
       with --esp flag, eg. '--esp /tmp'

    Returns:
        Mountpoint of EFI System Partition
    """
    partitions = [i.split() for i in read_cmd_list(('df', '-T'))]
    esp = None
    for partition in partitions:
        if partition[-1] == '/boot/efi':
            esp = partition[-1]
    if esp is None:
        for partition in partitions:
            if partition[-1] == '/boot' and partition[1] == 'vfat':
                esp = partition[-1]
    return esp


def get_paths(pkg_name: str, target_path: str) -> tuple:
    """Finds the absolute paths of the kernel and initrd from given package name.

    Args:
        pkg_name: Full name of a package.
        target_path: Path that dnf will use to install kernel & initrd
                     if it decides to install to ESP directly, mainly located
                     at /<ESP>/<MACHINE_ID>/
    Returns:
        A tuple with kernel's path at index 0 and initrd's path at index 1.
    """
    initrd = kernel = None
    pkg_files = read_cmd_list(('rpm', '-ql', pkg_name))
    boot_files = [f for f in pkg_files if '/boot' in f]
    for f in boot_files:
        output = read_cmd(('file', f))  # Try to determine files by their type.
        if 'cpio archive' in output:
            initrd = f
        elif 'Linux kernel' in output:
            kernel = f
    # In some situations, the kernel & initrd path found in the package doesn't
    # exist in the filesystem. The files will be found in /<ESP>/<MACHINE_ID>/
    # See /bin/kernel-install for specifics of this situation.
    if kernel is None or initrd is None:
        pkg_ver = pkg_name.replace('kernel-core-', '')
        kernel = f'{target_path}/{pkg_ver}/linux'
        initrd = f'{target_path}/{pkg_ver}/initrd'
    return (kernel, initrd)


# Checking for root.
if geteuid() != 0:
    print('This script must be run as root.')
    exit(1)


# Getting the full pkgname of kernel.
try:
    pkgs = read_cmd_list(('rpm', '-q', 'kernel-core'))
except CalledProcessError:
    print("You don't appear to have kernel installed.")
    exit(1)


# Determining the ESP.
try:
    esp = argv[argv.index('--esp') + 1]
except ValueError:
    esp = find_esp()


# Getting the Machine ID.
with open('/etc/machine-id') as id_file:
    target_path = esp + '/' + id_file.read().strip('\n')


# Get the paths of kernel and initrd.
pkg = get_paths(pkgs[-1], target_path)
kernel = target_path + pkg[0]
initrd = target_path + pkg[1]


# Create target directory if it doesn't exist
if not path.exists(esp + '/EFI/fedora/'):
    makedirs(esp + '/EFI/fedora/')


# Copy files to destination
copy2(pkg[0], esp + '/EFI/fedora/linux')
copy2(pkg[1], esp + '/EFI/fedora/initrd')
