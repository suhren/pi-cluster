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