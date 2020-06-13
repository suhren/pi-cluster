https://gist.github.com/geerlingguy/4613ea753d2286b6ed0cb4e3c272ce23


    curl https://gist.githubusercontent.com/geerlingguy/4613ea753d2286b6ed0cb4e3c272ce23/raw/a5deed4726a7da68e77b560c02f7b92d6da15f52/drupal.yml -o drupal.yml

    curl https://gist.githubusercontent.com/geerlingguy/4613ea753d2286b6ed0cb4e3c272ce23/raw/a5deed4726a7da68e77b560c02f7b92d6da15f52/mariadb.yml -o mariadb.yml


    kubectl create namespace drupal

    kubectl apply -f drupal.yml

    kubectl apply -f mariadb.yml

    watch kubectl get pods -n drupal -o wide

    kubectl get ingress -n drupal

Connect to the nip.io address to access the drupal installation!