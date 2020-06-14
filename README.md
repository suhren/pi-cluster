# pi-cluster

## Headless wireless setup:
https://www.raspberrypi.org/documentation/configuration/wireless/headless.md

1. Flash image (Debian Buster Lite)
1. Access boot directory of SD card
1. Follow the guide [here](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md) to setup the wireless connection. Create a file called `wpa_supplicant.conf` in the boot directory with the following contents
    
    ```
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=<Insert 2 letter ISO 3166-1 country code here>

    network={
        ssid="<Name of your wireless LAN>"
        psk="<Password for your wireless LAN>"
    }
    ```

1. Follow the guide [here](https://www.raspberrypi.org/documentation/remote-access/ssh/README.md) to setup the SHH connection. Simply create a file called `ssh` in the boot directory to enable SSH on boot so that we can connect.
1. Insert the SD card and wait! The setup might take some time. Keep an eye on your client list on your router or some other way of scanning your network and you should see that the new IP address of the PI should appear after some time. At this point it might still run some updates so wait for that to finish before connecting with SSH.
1. Note: I kept getting the "Destination host unreachable" when attempting to ping the PI after installation. I actually had to restart my home router to make sure that the connection worked with the PI. I think the error might have been that the PI was connected to the 5GHz or perhaps the guest network instead of the main network.

## Diagnostics

Check temperature:

    vcgencmd measure_temp

Check if throttled:

    vcgencmd get_throttled

## Setup

This setup is based on [this video tutorial](https://www.youtube.com/watch?v=B2wAJ5FLOYw) by Jeremey LaCroix `LearnLinuxTV`. He also has a web site at jaylacroix.com.

1. Insert the empty SD card in your main computer
1. Flash image (Debian Buster Lite)
1. Remove the card and insert it again
1. Run either `df -h` or `lsblk` to make sure we can see the two mount points `boot` and `rootfs`
1. Run `cd /run/media/<user>/boot`
    
We can create a file called `ssh` to enable SSH by default:

    touch ssh

Then

    cd /run/media/<user>/rootfs
    cd etc/
    sudo nano hostname

The default hostname is `raspberrypi`. We can change this to something better like 

    rpic-master
    rpic-worker-01
    rpic-worker-02
    rpic-worker-03

Then

    sudo nano hosts

Change the name here as well.

    cd ~

And remove the SD card. We can repeat these steps for the remaining PIs.

## Local machine
https://dev.to/awwsmm/building-a-raspberry-pi-hadoop-spark-cluster-8b2

Open the file `/etc/hosts` and add

    192.168.127.101 rpic-master
    192.168.127.102 rpic-worker-01
    192.168.127.103 rpic-worker-02
    192.168.127.104 rpic-worker-03

Create the file `~/.ssh/config` with the following content:

    Host rpic-master
    User pi
    Hostname 192.168.127.101

    Host rpic-worker-01
    User pi
    Hostname 192.168.127.102

    Host rpic-worker-02
    User pi
    Hostname 192.168.127.103

    Host rpic-worker-03
    User pi
    Hostname 192.168.127.104

Now we can setup public/private key pairs for each pi:

    cd ~/.ssh
    ssh-keygen

For each PI:

    ssh-copy-id <USERNAME>@<IP-ADDRESS>

If there is a problem with old keys:

    ssh-keygen -f "/home/<USERNAME>/.ssh/known_hosts" -R "<IP-OF-PI>"

We can make our lives even easier with some aliases. In the file `~/.bashrc` add the lines

    alias rpic-master="ssh rpic-master"
    alias rpic-worker-01="ssh rpic-worker-01"
    alias rpic-worker-02="ssh rpic-worker-02"
    alias rpic-worker-03="ssh rpic-worker-03"

Also in `.bashrc`, we can add the following functions which will list each Pi in the cluster and also allow us to issue commands to them all at once:

    function rpic-list {
        grep "pi" /etc/hosts | awk '{print $2}' | grep -v $(hostname)
    }

    function rpic-cmd {
        for pi in $(rpic-list); do printf "\n$pi:\n"; ssh $pi "$@"; done
    }

    function rpic-ping {
        for pi in $(rpic-list); do ping -w 1 $pi &>/dev/null && echo $pi success || echo $pi fail; done
    }

    function rpic-reboot {
        rpic-cmd "sudo shutdown -r now"
    }

    function rpic-shutdown {
        rpic-cmd "sudo shutdown now"
    }

    function rpic-scp {
        for pi in $(rpic-list); do
            cat $1 | ssh $pi "sudo tee $1" > /dev/null 2>&1
        done
    }

Then we can run commands on all nodes in the cluster with e.g.

    rpic-cmd date
    rpic-cmd "{ hostname & date; } | cat"
    rpic-cmd "sudo reboot now"


## SSH

Find the hostnames of the PIs in e.g. your router DHCP table

Run `ssh pi@<ip-address>`

For each raspberry pi:

    sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove -y && sudo apt-get autoclean

Then

    sudo nano /boot/cmdline.txt

Append

    cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory

If we do `free -m` we should see that there is Swap space available. We don't want any when we are going to use Kubernetes.

    sudo dphys-swapfile swapoff

Now `free -m` should show 0 for the swap. It will however come back after reboot so we need to make sure it is gone permanently:

    sudo dphys-swapfile uninstall; sudo apt purge dphys-swapfile -y

Then run `sudo reboot` and wat for the PIs to come back up. SSH back into them and install docker:

    curl -sSL get.docker.com | sh

Then

    sudo usermod -aG docker pi
    logout

Then SSH back in.

    sudo nano /etc/docker/daemon.json

Add the following:

    {
        "exec-opts": ["native.cgroupdriver=systemd"],
        "log-driver": "json-file",
        "log-opts": {
            "max-size": "100m"
        },
        "storage-driver": "overlay2"
    }

Then run `sudo reboot` again.

    sudo nano /etc/apt/sources.list.d/kubernetes.list

Add

    deb http://apt.kubernetes.io/ kubernetes-xenial main

We now need the key which we can get with

    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

Then run 

    sudo apt update
    sudo apt install kubeadm kubectl kubelet -y

Note, you may have to rerun the previous command (update) a few times if you get the error `Some index files failed to download. They have been ignored, or old ones used instead.`

Now, only run this command for the **MASTER**:

    sudo kubeadm init --pod-network-cidr=10.17.0.0/16 --service-cidr=10.18.0.0/24 --extra-config=kubelet.authentication-token-webhook=true --extra-config=kubelet.authorization-mode=Webhook

or the following if you have a domain:

    sudo kubeadm init --pod-network-cidr=10.17.0.0/16 --service-cidr=10.18.0.0/24 --service-dns-domain=mydomain.com

This command can take a while. After it is done there should be an output which looks like

    kubeadm join <ip-address> --token <token> ...

Copy that text and save it somewhere safe. With that command it is possible for any node to join this cluster, perhaps even rogue nodes you don't control!

Then, again on the master, run:

    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config

Now we want to install a network driver on the master:

    kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

Then on the master

    kubectl get pods --all-namespaces

The STATUS of all pods should be RUNNING.

Now we can let the other nodes join the cluster. We do this by running

    sudo <the-join-command-you-saved-earlier>

Check if they have joined by

    kubectl get nodes


## Laptop as DHCP
Partially based on a guide by [Paloseco](https://ubuntuforums.org/showthread.php?t=2379769):

Internet < ----- > Router-192.168.0.1 [RJ45] < ---- > [eth0] PC1-192.168.0.x [eth1] < ---- > [eth2] PC2-192.168.127.x

### Step 1: IP forwarding
Enable IP forwarding on computer 1:
    
    sudo echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward

### Step 2: IP tables

    sudo /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    sudo /sbin/iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
    sudo /sbin/iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT

### Step 3: IP for eth1

    sudo ifconfig eth1 192.168.127.1 netmask 255.255.255.0

### Step 4: DHCP server

    sudo apt-get install isc-dhcp-server
    sudo sed -i '/INTERFACESv4=/c\INTERFACESv4=\"eth1\"' /etc/default/isc-dhcp-server

    subnet 10.0.0.0 netmask 255.255.255.0 { 
        authoritative; 
        range 10.0.0.30 10.0.0.60;  
    }

Edit `/etc/dhcp/dhcpd.conf` so it looks like that:

    subnet 192.168.127.0 netmask 255.255.255.0 {
        interface enp0s31f6;
        range 192.168.127.100 192.168.127.200;
        option subnet-mask 255.255.255.0;
        option routers 192.168.127.1;
        option broadcast-address 192.168.127.255;
        option domain-name-servers 8.8.8.8, 8.8.4.4;
        option domain-name "rpic.lab";
        default-lease-time 600;
        max-lease-time 7200;
        ddns-update-style none;
    
        host server {
            hardware ethernet 8c:16:45:11:af:81;
            fixed-address 192.168.127.1;
        }
        host rpic-master {
            hardware ethernet dc:a6:32:70:d5:2b;
            fixed-address 192.168.127.101;
        }
        host rpic-worker-01 {
            hardware ethernet dc:a6:32:50:f0:56;
            fixed-address 192.168.127.102;
        }
        host rpic-worker-02 {
            hardware ethernet dc:a6:32:4c:06:08;
            fixed-address 192.168.127.103;
        }
        host rpic-worker-03 {
            hardware ethernet dc:a6:32:70:cc:ac;
            fixed-address 192.168.127.104;
        }
    }

### Step 5: Run DHCP server

    sudo ifconfig eth1 down
    sudo ifconfig eth1 up
    sudo service isc-dhcp-server restart

### Step 6: Startup script

    sudo echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
    sudo /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    sudo /sbin/iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
    sudo /sbin/iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT
    sudo ifconfig eth1 192.168.127.1 netmask 255.255.255.0
    sudo ifconfig eth1 down
    sudo ifconfig eth1 up
    sudo service isc-dhcp-server restart

Change permissions and move to sbin:

    sudo cp sharepc1.sh /usr/local/sbin/sharepc1.sh
    sudo chmod 777 /usr/local/sbin/sharepc1.sh

### Other useful commands

Find the name of your wired ethernet interface with the command:

    sudo lshw -C network
    ifconfig

Then we start the server with

    sudo systemctl start isc-dhcp-server.service

and we can check the status with

    sudo systemctl status isc-dhcp-server.service
    sudo journalctl -fu isc-dhcp-server.service

If there is a problem you can use

    sudo systemctl stop isc-dhcp-server.service
    sudo systemctl restart isc-dhcp-server.service

The devices should now be assigned an IP address which can be listed with the command

    dhcp-lease-list

Flush DHCP leases:

    sudo rm -f var/lib/dhcp/dhcpd.leases
    sudo rm -f var/lib/dhcp/dhcpd.leases~

## Notes

I actually had a problem initially with the master node of my cluster being very slow compared to the other nodes. It lead to problems with e.g. running `kubeadm init` timing out due to the node being so slow. After some testing I tried replacing the SD card with another identical one (Toshiba M203 32GB) and it worked, and was lot faster!


## docker login issue with docker-compose on ARM
https://github.com/docker/compose/issues/6023


# k3s

https://k3s.io/

## Install Ansible:

    sudo apt update
    sudo apt install software-properties-common
    sudo apt-add-repository --yes --update ppa:ansible/ansible
    sudo apt install ansible


## Generate SSH keys and share with PIs

    cd ~/.ssh
    ssh-keygen

For each PI:

    ssh-copy-id <USERNAME>@<IP-ADDRESS>

If there is a problem with old keys:

    ssh-keygen -f "/home/<USERNAME>/.ssh/known_hosts" -R "<IP-OF-PI>"

## Use Ansible:

    cd ~/git
    git clone https://github.com/rancher/k3s-ansible
    cd k3s-ansible

Due to a bug in the (at the time) newest relase causing this error:

    fatal: [192.168.127.101]: FAILED! => {"msg": "The conditional check 'raspbian is true' failed. The error was: template error while templating string: no test named 'true'. String: {% if raspbian is true %} True {% else %} False {% endif %}\n\nThe error appears to be in '/home/suhren/git/k3s-ansible/roles/raspbian/tasks/main.yml': line 10, column 3, but may\nbe elsewhere in the file depending on the exact syntax problem.\n\nThe offending line appears to be:\n\n\n- name: Activating cgroup support\n  ^ here\n"}

I had to revert back to an older commit:

    git checkout 5d92b0ac41ec56b370301fd2fb6d6cccee98e020

Fill the `hosts.ini` with the IPs of your PIs and make sure it is located in `inventory/hosts.ini`.

Change the username from `debian` to the user of the PIs (default `pi`) in the file `inventory/group_vars/all.yml`. Due to another bug at the time, I also had to move the directory `group_vars/all.yml` to the root.


Copy the kube config file to your local machine:

    mkdir ~/.kube
    scp pi@192.168.127.101:~/.kube/config ~/.kube/config-rpic

Install kubectl:

    sudo nano /etc/apt/sources.list.d/kubernetes.list

Add

    deb http://apt.kubernetes.io/ kubernetes-xenial main

We now need the key which we can get with

    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

Then run 

    sudo apt update
    sudo apt install kubectl

Then set the path to the config file:

     export KUBECONFIG=~/.kube/config-rpic

Then test the kubectl with

    kubectl version

### Useful commands

Shut down all PIs:

    ansible all -i inventory/hosts.ini -a "shutdown now" -b