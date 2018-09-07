# Fedora Installation Via Chroot

Scripts and guides for installing [Fedora](https://getfedora.org) via a chroot from a live system. Like you'd do in [Installing Debian GNU/Linux from a Unix/Linux System](https://www.debian.org/releases/stable/amd64/apds03.html.en)
or installing [Arch Linux](https://archlinux.org).

## Common Things to Do

1. Get a Fedora Workstation image [from here](https://getfedora.org/en/workstation/download/).

2. Get comfortable with the live system. Configure network, keyboard layout, get root etc.

3. Disable selinux temporarily

       # setenforce 0

## Notes

    # denotes the commands to be run as the root user.
    $ denotes the commands to be run as a regular user or the root user.
    No denotation means regular user commands which don't have an output.
    <TEXT> fields should be customized by the user.
    (chroot) denotes the commands to be run in chroot.

## Guides

* [Installing on an UEFI Virtual Machine](docs/VM-Install.md)
