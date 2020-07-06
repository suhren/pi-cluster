# Pi-hole

https://github.com/MoJo2600/pihole-kubernetes

```bash
helm repo add mojo2600 https://mojo2600.github.io/pihole-kubernetes/
helm repo update
```

```bash
kubectl create namespace pihole
```

```bash
helm install --version '1.7.6' --namespace pihole --values pihole.yml pihole mojo2600/pihole
```

```bash
watch kubectl get pods -n pihole
```