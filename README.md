# Proxmox to Nextcloud TALK bridge
This little python app will enable your Proxmox PVE or PBS to send notifications to your desired Nextcloud talk room. You don´t need a nextcloud bot or another addon or plugin. You can already use webhook targets in stock Proxmox, so will make use of this feature. What I want to say is, all you need is a Proxmox Host, a nextcloud talk and an debian/ubuntu lxc/vm and you my friend are ready to rock!

## Requirements
* Proxmox PVE or PBS
* Nextcloud with Nextcloud Talk
* Debian or Ubuntu LXC/VM

## Setup
1. We will first prepare a user with an app password on our nextcloud and add him to the target room
2. We will setup the python app and systemd service on the lxc/VM
3. We will configure the webhook target on proxmox
4. Optional: We will monitor the app via Uptime Kuma
