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


## Setup

1. Insert the empty SD card in your main computer
1. Flash image (Debian Buster Lite)
1. Remove the card and insert it again
1. Run either `df -h` or `lsblk` to make sure we can see the two mount points `boot` and `rootfs`
1. Run `cd /run/media/<user>/boot`
    
We can create a file called `ssh` to enable SSH by default:

    touch ssh

Then

    cd /run/media/<user>/rootfs
    cd /etc
    sudo nano hostname

The default hostname is `raspberrypi`. We can change this to something better like 

    rpi-0
    rpi-1
    rpi-2
    rpi-3

Then

    sudo nano hosts

Change the name here as well.

    cd ~

And remove the SD card. We can repeat these steps for the remaining PIs.

## SSH

Find the hostnames of the PIs in e.g. your router DHCP table

Run `ssh pi@<ip-address>`

For each raspberry pi:

    apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

Then

    sudo nano /boot/cmdline.txt

Append

    cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory

If we do `free -m` we should see that there is Swap space available. We don't want any when we are going to use Kubernetes.

    sudo dphys-swapfile swapoff

Now `free -m` should show 0 for the swap. It will however come back after reboot so we need to make sure it is gone permanently:

    sudo dphys-swapfile uninstall
    sudo apt purge dphys-swapfile

Then run `sudo reboot` and wat for the PIs to come back up. SSH back into them and install docker:

    curl -sSL get.docker.com | sh

Then

    sudo usermod -aG docker pi
    logout

Then SSH back in.

    sudo nano /etc/docker/daemon.json

Add the following:

    {
        "exec-opts": ["native.cgroupdriver=systemd],
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

Then

    sudo apt install kubeadm kubectl kubelet -y

Now, only run this command for the **MASTER**:

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

    