#!/usr/bin/env bash

function install_mysql(){
    yum install -y mariadb-server
    systemctl enable mariadb
}

function install_python(){
    yum install -y python3 python3-setuptools 
}

function install_nginx() {
    yum install -y nginx
    systemctl enable nginx
}

install_mysql
install_python
install_nginx

pip3 install -r requirements.txt

rm -f /usr/local/lib/python3.6/site-packages/dj_pagination/templates/pagination/pagination.html
cp templates/zde/pagination.html /usr/local/lib/python3.6/site-packages/dj_pagination/templates/pagination
