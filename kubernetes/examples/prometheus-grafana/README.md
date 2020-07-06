
On the master node:

```bash
git clone https://github.com/carlosedp/cluster-monitoring
```

**For k3s:**
In the file `vars.jsonnet`change the value `enabled` from `false` to `true` and change the `master_ip` to the ip of the master node.

Change `suffixDomain` to the ip address of one of the worker nodes (`XXX.XXX.XXX.XXX.nip.io`).

Also enable the `armExporter` to get data about CPU temperature and other ARM-related features.

Then run:

```bash
sudo apt-get update
sudo apt-get install -y build-essential golang
```

Then it is time to `make` the project. In the cloned git repo, run:

```bash
make vendor
make
kubectl apply -f manifests/setup/
kubectl apply -f manifests/
```

Now we can watch our nodes to see what happens:

```bash
kubectl get pods -n monitoring
```

or the following command to watch them update continuously

```bash
watch kubectl get pods -n monitoring
```

Find the ingress name which kubernetes provides to let us access the Prometheus service:

```bash
kubectl get ingress -n monitoring
```

```bash
kubectl logs -f -n monitoring prometheus-adapter-f78c4f4ff-6jm2f -c prometheus-operator
```

```bash
kubectl delete -f manifests/setup
kubectl delete -f manifests/
```

```bash
kubectl get ingress --all-namespaces
```

### Notes:

Problem with the `prometheus-operator-xxx`pod:

```
err="communicating with server failed: Get https://10.18.0.1:443/version?timeout=32s: dial tcp 10.18.0.1:443: i/o timeout"
```

This was due to initializing `kubeadm`with the default

```bash
sudo kubeadm init --pod-network-cidr=10.17.0.0/16 --service-cidr=10.18.0.0/24
```

This caused an IP collision. I found this out through this thread: https://github.com/rancher/rancher/issues/10322

The solution is to use another IP range, like

```bash
sudo kubeadm init --pod-network-cidr=172.17.0.0/16 --service-cidr=172.18.0.0/24
```