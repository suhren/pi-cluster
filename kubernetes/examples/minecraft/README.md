# Minecraft deployment

## Install helm
https://helm.sh/docs/intro/install/

```bash
ssh pi@192.168.127.101

wget https://get.helm.sh/helm-v3.2.3-linux-arm.tar.gz
tar -zxvf helm-v3.2.3-linux-arm.tar.gz
sudo mv linux-arm/helm /usr/local/bin/helm

helm help
```

Note: I tried using the version `v2.16.8` at first, but that did not work as the `tiller` service was not starting correctly: `Could not find a ready tiller pod (Error)`

## Minecraft

https://github.com/helm/charts

```bash
helm repo add stable https://kubernetes-charts.storage.googleapis.com
```

Make sure you have run `export KUBECONFIG=~/.kube/<config-name>`. 
    
https://github.com/helm/charts/tree/master/stable/minecraft

```bash
helm install --version '1.2.2' --namespace minecraft --values minecraft.yml minecraft stable/minecraft
```

Get the external IP to the server using the command

```bash
kubectl get svc --namespace minecraft -w minecraft-minecraft
```

You can also look at the logs of the server with

```
kubectl get pods -n minecraft
```

```
kubectl logs -f -n minecraft minecraft-minecraft-5b9bc8849d-kwxz4
```