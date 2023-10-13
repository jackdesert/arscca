Configure Alma (Ran into issues where `yum install` would be killed....out of memory??
================

(Lesley suggests running these as root instead of as sudo...)
(/usr/bin is in root's path, but /usr/local/bin is not)
(or could write direct to /usr/bin)

(Ran into issues where `yum install` would be killed....out of memory??
Also challenges getting docker to run...supposedly RHEL is pushing podman instead.
(I infer you can run podman with docker images...??)

Giving up for now: let's try ubuntu

Create Droplet
--------------

Create a droplet: almalinux 9


Create user account
-------------------

From web-based terminal:

    # create user
    adduser  --shell /bin/bash alma

    # add to wheel (instead of sudoers) group
    usermod -G wheel alma

    # enable passwordless sudo
    # Add the next line after the  `root ALL=(ALL)` line
    # alma ALL=(ALL) NOPASSWD:ALL
    #
    # Also add /usr/local/bin to the secure_path in visudo (otherwise you cannot sudo docker-compose)
    visudo

    # become alma so you can set up key
    sudo su alma
    cd
    mkdir .ssh
    vi .ssh/authorized_keys
    # add your public key

Docker
------

https://orcacore.com/install-use-docker-almalinux-9/

Log in as alma

    sudo dnf update -y && sudo dnf upgrade -y

    # Enable additional packages
    sudo yum install -y epel-release

    # remove podman and buildah
    sudo yum remove -y podman buildah

    # Add repo
    sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo


    sudo dnf install -y docker-ce docker-ce-cli containerd.io    git
    sudo systemctl start docker.service
    sudo systemctl enable docker.service

    sudo usermod -aG docker $(whoami)

(you can run docker as sudo for now until I figure out how to enable without...so far there is not docker group)

Docker compose:
see https://orcacore.com/install-docker-compose-almalinux-8/

    sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose


git clone
---------

    git clone git@github.com:jackdesert/arscca
    git clone git@github.com:jackdesert/arscca-twisted
