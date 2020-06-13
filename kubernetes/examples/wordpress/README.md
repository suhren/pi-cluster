# Wordpress deployment

https://gist.github.com/geerlingguy/e6a661e1cd2b53f6a39493ebb207425c


    curl https://gist.githubusercontent.com/geerlingguy/e6a661e1cd2b53f6a39493ebb207425c/raw/79df0cce9738c7fd5fd2b941944a2c2ec20f3c23/wordpress.yml -o wordpress.yml

    curl https://gist.githubusercontent.com/geerlingguy/e6a661e1cd2b53f6a39493ebb207425c/raw/79df0cce9738c7fd5fd2b941944a2c2ec20f3c23/mariadb.yml -o mariadb.yml


Change the host name to one of your worker nodes, like `wordpress.192.168.127.102.nip.io`

Then run:

    kubectl create namespace wordpress

    kubectl apply -f wordpress.yml

    kubectl apply -f mariadb.yml

    watch kubectl get pods -n wordpress -o wide

    kubectl get ingress -n wordpress

Connect to the `nip.io` address to access the wordpress installation!