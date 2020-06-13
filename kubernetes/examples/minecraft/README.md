# Minecraft deployment

## Install helm
https://helm.sh/docs/intro/install/

    ssh pi@192.168.127.101

    wget https://get.helm.sh/helm-v2.16.8-linux-arm.tar.gz
    tar -zxvf helm-v2.16.8-linux-arm.tar.gz
    sudo mv linux-arm/helm /usr/local/bin/helm

    helm help

## Minecraft

https://github.com/helm/charts

    helm repo add stable https://kubernetes-charts.storage.googleapis.com
    
https://github.com/helm/charts/tree/master/stable/minecraft

