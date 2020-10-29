#!/usr/bin/env bash

function install_mysql(){
    yum install -y mariadb-server
    systemct enable mariadb
}

function install_python(){
    yum install -y python3 python3-setuptools 
}

function install_nginx() {
    yum install -y nginx
    systemctl enable nginx
}

rm -f /usr/local/lib/python3.6/site-packages/dj_pagination/templates/pagination/pagination.html
cp templates/zde/pagination.html /usr/local/lib/python3.6/site-packages/dj_pagination/templates/pagination
pip3 install -r requirements.txt
