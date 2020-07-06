https://gist.github.com/geerlingguy/4613ea753d2286b6ed0cb4e3c272ce23


```bash
curl https://gist.githubusercontent.com/geerlingguy/4613ea753d2286b6ed0cb4e3c272ce23/raw/a5deed4726a7da68e77b560c02f7b92d6da15f52/drupal.yml -o drupal.yml
```

```bash
curl https://gist.githubusercontent.com/geerlingguy/4613ea753d2286b6ed0cb4e3c272ce23/raw/a5deed4726a7da68e77b560c02f7b92d6da15f52/mariadb.yml -o mariadb.yml
```

```bash
kubectl create namespace drupal
```

```bash
kubectl apply -f drupal.yml
kubectl apply -f mariadb.yml
```

```bash
watch kubectl get pods -n drupal -o wide
```

```bash
kubectl get ingress -n drupal
```

Connect to the nip.io address to access the drupal installation!