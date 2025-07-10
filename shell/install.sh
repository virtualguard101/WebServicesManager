#!/bin/bash
set -ue
sudo apt update

## Docker
# curl -fsSL https://get.docker.com | bash -s docker
# sudo apt install docker-compose
# # sudo groupadd docker # 若尚不存在 docker 组，则需先创建
# sudo usermod -aG docker $USER

## Nginx
sudo apt install nginx
sudo systemctl enable nginx

## Certbot
sudo apt install certbot

## Cron
sudo apt install cron

## Python
sudo apt install python3
sudo apt install pip
curl -LsSf https://astral.sh/uv/install.sh | sh   # astral uv
