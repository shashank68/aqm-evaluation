#!/bin/bash
# Enables the passwordless ssh connection between the specified client and the router

client_ns=${1}
router_ns=${2}
router_ssh_address=${3}

ip netns exec ${router_ns} /usr/sbin/sshd

if ! [ -e /home/${SUDO_USER}/.ssh/id_rsa ] || ! [ -e /home/${SUDO_USER}/.ssh/id_rsa.pub ]
then
    ssh-keygen -A > /dev/null

    echo y | sudo -u ${SUDO_USER} ssh-keygen -q -t rsa -f /home/${SUDO_USER}/.ssh/id_rsa -N "" > /dev/null
fi

cat /home/${SUDO_USER}/.ssh/authorized_keys 2> /dev/null | grep "$(cat /home/${SUDO_USER}/.ssh/id_rsa.pub)" > /dev/null

if [ ${?} -ne 0 ]
then
    sudo -u ${SUDO_USER} bash -c "cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys"
fi

ip netns exec ${client_ns} sudo -u ${SUDO_USER} bash -c "ssh-keyscan -4 -t rsa ${router_ssh_address} >> ~/.ssh/known_hosts 2> /dev/null"
