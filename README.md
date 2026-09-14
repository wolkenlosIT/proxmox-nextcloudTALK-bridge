# Proxmox to Nextcloud TALK bridge
This little python app will enable your Proxmox PVE or PBS to send notifications to your desired Nextcloud talk room. You don´t need a nextcloud bot or another addon or plugin. You can already use webhook targets in stock Proxmox, so will make use of this feature. What I want to say is, all you need is a Proxmox Host, a nextcloud talk and an debian/ubuntu lxc/vm and you my friend are ready to rock!

## Requirements
* Proxmox PVE or PBS
* Nextcloud with Nextcloud Talk
* Debian or Ubuntu LXC/VM

## Setup
1. We will first prepare a service account with an app password on our nextcloud and add him to the targeted room
2. We will setup the python app and systemd service on the lxc/VM
3. We will configure the webhook target on proxmox
4. Optional: We will monitor the app via Uptime Kuma

### Nextcloud setup
1. Create a new user
2. If you don´t already have a nextcloud talk channel for your notifications create one
3. Add the new user to the channel
4. Copy the channel id. To do so enter the channel. You just need to copy the last part of the url. For example if your url is *https://nextcloud.pizzaparty.lan/call/xvq3a88p* you need to copy the *xvq3a88p*
5. Logout and login as the new user
![NextcloudAPPtoken](https://github.com/wolkenlosIT/proxmox-nextcloudTALK-bridge/blob/main/setupimages/nextcloudapptoken.jpg)
6. Click on your profil pic ---> Click on Settings ---> Click on Security --> Scroll down to *Devices & sessions* and enter an App Name --> Click on *Generate new app password*
7. The popup will present you the password. Copy it. We will need it in the next step
8. Optional: If you want to add an avatar to the service account. Now is a good time to do so!
