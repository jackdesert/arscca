Configure Ubuntu
================

Create VPS
--------------

Create a droplet: ubuntu 18.04 LTS with docker (racknerd)


Create user account
-------------------

From root terminal:

    sudo apt update -y && apt install -y screen htop nginx python3-venv rsync

    # Create two non-root user:
    #   - one for normal login (MORTAL)
    #   - one named arscca
    MORTAL=ubuntu
    # Note --comment is supposed to make it non-interactive
    adduser  --shell /bin/bash --disabled-password --comment 'main_login' $MORTAL
    adduser  --shell /bin/bash --disabled-password --comment 'for_laptop_push' arscca

    # add to sudoers group
    usermod -a -G sudo $MORTAL

    # enable passwordless sudo
    # Allow members of group sudo to execute any command
    # Add `NOPASSWD` so it looks like this:
    #      %sudo   ALL=(ALL:ALL) NOPASSWD:ALL
    visudo

    # become alma so you can set up key
    sudo su $MORTAL
    cd
    mkdir .ssh
    vi .ssh/authorized_keys
    # add your public key
    vi .bashrc

    export PAGER='less -i'
    export EDITOR=vi
    alias jack1='screen -D -R jack1'
    alias gu='git fetch origin && git rebase origin/master'
    alias log='git log --name-status'
    alias sb='source ~/.bashrc'
    alias alie='vi ~/.bashrc'
    alias bs='git branch && git status'


Docker
------

Docker is already installed, but docker-compose is not.

https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04

    sudo curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    docker-compose --version

    # Make it so you can run passwordless docker
    sudo usermod -aG docker $(whoami)
    # Restart shell so change takes effect
    exit

git clone
---------

    git clone git@github.com:jackdesert/arscca
    git clone git@github.com:jackdesert/arscca-twisted
    git config --global user.name 'Jack Desert'
    git config --global user.email 'JackDesert'



Config Files
------------

Create the following config files

    cd arscca/config
    cp user_passwords.json-EXAMPLE user_passwords.json
    cp aws_credentials.json-EXAMPLE aws_credentials.json


Docker Networks & Volumes
-------------------------

    docker volume create arscca-redis-data
    docker network create arscca-network
    jack1
    cd ~/arscca

    # Create WATCHED_FILENAME for arscca-twisted
    WATCHED_FILENAME=/home/arscca/arscca-live.jinja2
    sudo touch $WATCHED_FILENAME
    sudo chown ubuntu:www-data $WATCHED_FILENAME

    # Create ARCHIVE_DIR for arscca-twisted (writable by ubuntu via www-data group)
    ARCHIVE_DIR=/home/arscca/archive
    sudo mkdir -p $ARCHIVE_DIR
    sudo chown -R ubuntu:www-data $ARCHIVE_DIR

    # These log files apparently need to exist in order to bind them in docker-compose.yml
    # (perhaps this is due to new version of docker-compose?)
    touch /tmp/arscca-pyramid.log /tmp/arscca-twisted.log

    docker-compose up

Nginx
-----

    cd /etc/nginx/sites-enabled
    sudo ln -s ~/arscca/config/nginx-arscca__tcp-socket.conf
    sudo nginx -s reload

arscca authorized_keys
----------------------

Copy the public key from the club laptop and put it in arscca authorized keys

    sudo -u arscca  mkdir -p /home/arscca/.ssh
    sudo su arscca
    echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDIJY0RGrCWxmNBQGckor+rULNa6m/i7SIs0imfbGwE1dYUSNgUlz/P4XIKNQZMzP7jIrwEmsmS+D7TMcRkzvhbda7eqilL9ADw4Ahhpizn0T/8yP1lkNneZqH54s3KnmcIKc+wpcAte02coc94RX3AZcmHZKzNKPs+AeWMe4jzev2cRCRNF3aS2yNBPjghQVQxTcK05tFXUGQkFI8cxhdU59R70ypikBFLmpBp51ybWnp5cIuXAkPidHdXs2xeTav5yKEB72rAeLFwq2FMrMvVI+tXl4wRcj3urMMknlLwf5Iic+gN26enH1kFeiWquK373HzxUNxlC1LdR/WD5InX User@MININT-EO6EKSC' >> /home/arscca/.ssh/authorized_keys
    exit

Cron Job
--------

    # configure a simple virtualenv for running cron job
    VENV=~/simple-venv
    python3 -m venv $VENV && \
    $VENV/bin/pip install requests==2.23.0 bs4==0.0.1 pytz==2019.3 lxml==4.6.2

Now write a cronjob and put the following in it:

    #! /bin/bash
    LOG=/tmp/cron.log
    YEAR=$(date +'%Y')
    */15 * * * * cd /home/ubuntu/arscca && /home/ubuntu/simple-venv/bin/python bin/archive_events.py "$YEAR"  >> $LOG  2>&1



Screen
------

Open screen, then run:

    docker-compose up


Things to have them Test
------------------------

1. Live results push
2. Msreg page

