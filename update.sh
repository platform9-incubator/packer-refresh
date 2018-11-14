#!/bin/bash
if [ -n "$(command -v yum)" ]; then
  sudo yum update -y
  echo '' | sudo tee /home/centos/.ssh/authorized_keys
elif [ -n "$(command -v apt-get)" ]; then
  sudo apt-get update -y
  sudo apt-get upgrade -y
  sudo apt-get dist-upgrade -y
  echo '' | sudo tee /home/ubuntu/.ssh/authorized_keys
else
  exit 1
fi
echo '' | sudo tee /root/.ssh/authorized_keys
