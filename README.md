# Proxmox to Nextcloud TALK bridge
This little python app will enable your Proxmox PVE or PBS to send notifications to your desired Nextcloud talk room. You don´t need a nextcloud bot or another addon or plugin. Also, we will make use of webhook targets in stock Proxmox. What I want to say is, all you need is a Proxmox Host, a nextcloud talk and an debian/ubuntu lxc/vm and you my friend are ready to rock!

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
2. If you don´t already have a nextcloud talk channel for your notifications, create one
3. Add the new user to the channel
4. Copy the channel id. To do so enter the channel. You just need to copy the last part of the url. For example if your url is *https://nextcloud.pizzaparty.lan/call/xvq3a88p* you need to copy the *xvq3a88p*
5. Logout and login as the new user
![NextcloudAPPtoken](https://github.com/wolkenlosIT/proxmox-nextcloudTALK-bridge/blob/main/setupimages/nextcloudapptoken.jpg)
6. Click on your profile pic ---> Click on Settings ---> Click on Security --> Scroll down to *Devices & sessions* and enter an App Name --> Click on *Generate new app password*
7. The popup will present you the password. Copy it. We will need it in the next step
8. Optional: If you want to add an avatar to the service account: Now is a good time to do so!
9. With this the setup on your nextcloud is completed

### Python app setup
1. Log into your debian or ubuntu lxc/vm with root or a sudo user
2. Let´s create the app first. Our working dictionary will be:
```shell
sudo mkdir /opt/proxmox-talk-bridge
```
3. Copy/past the app.py or download it to the directory. You don´t have to change anything here.
```shell
sudo nano /opt/proxmox-talk-bridge/app.py
```
(Optional: The notification proxmox sends can be quiet long. This is why I let the python script cut the message after 600 characters. If you want more or less, you can change the number in line 181.)

5. Let´s create the webhook secret:
```shell
openssl rand -hex 16
```
6. Copy the secret and let´s create our environments file. Fill it out, too!
```shell
sudo nano /etc/proxmox-talk-bridge.env
```
7. Let´s add a user, group and change the permission to our files, so that we can let the app run as a non root user:
```shell
sudo groupadd --system proxmox-talk
sudo useradd --system --gid proxmox-talk --home-dir /opt/proxmox-talk-bridge --shell /usr/sbin/nologin proxmox-talk
sudo chown -R proxmox-talk:proxmox-talk /opt/proxmox-talk-bridge
sudo chown root:proxmox-talk /etc/proxmox-talk-bridge.env
sudo chmod 640 /etc/proxmox-talk-bridge.env
```
8. The next step is the creation of a systemd service:
```shell
sudo nano /etc/systemd/system/proxmox-talk-bridge.service
```
9. Reload the deamon and enable the service for an autostart:
```shell
sudo systemctl daemon-reload
sudo systemctl enable proxmox-talk-bridge.service
```
10. You can now start the app via systemd and check the status:
```shell
sudo systemctl start proxmox-talk-bridge.service
sudo systemctl status proxmox-talk-bridge.service
```
11. You can check with the following if the webservice is reachable:
```shell
curl -i http://127.0.0.1:8788/health
```
12. With this. We can move to one of our proxmox servers!

### Proxmox setup
1. Log into your Proxmox and click on Datacenter.
2. Scroll down and click on Notifications
3. Under "Notification Targets" click on "Add" and select "Webhook"
![proxmoxwebhooksetup1](https://github.com/wolkenlosIT/proxmox-nextcloudTALK-bridge/blob/main/setupimages/proxmoxwebhooksetup1.jpg)
4. Add a Endpoint name. Whatever you like
5. Under "Method/URL" select "POST" and add your lxc/vm url in the following format: http://SWAP_WITH_YOUR_LXC_IP_ADRESS:8788/proxmox
6. Under Headers add a Header with the key: "X-Proxmox-Webhook-Secret" and the value, which is the webhook secret you created in the last part.
7. Copy and paste the following into "Body":
```shell
{
"title":"{{ escape title }}",
"message":"{{ escape message }}",
"severity":"{{ escape severity }}",
"timestamp":{{ timestamp }},
"fields":{{ json fields }}
}
```
8. Safe
![proxmoxwebhooksetup2](https://github.com/wolkenlosIT/proxmox-nextcloudTALK-bridge/blob/main/setupimages/proxmoxwebhooksetup2.jpg)
9. Select your Target and click on Test. If everything is working you should have received in your Nextcloud Talk room
10. Under Notification Matcher you can add your newly created webhook target, so that you get all or whatever notifications you desire to your Nextcloud.
![proxmoxwebhooksetup3](https://github.com/wolkenlosIT/proxmox-nextcloudTALK-bridge/blob/main/setupimages/proxmoxwebhooksetup3.jpg)
11. If you have multiple PVEs or PBSs, you just simply have to repeat the Proxmox Setup on each of them. There is no change on the lxs/vm or nextcloud. The nextcloud message will always say which server is sending the message

### Monitor the bridge with Uptime Kuma
1. Log into your Uptime Kuma
2. Add a new monitor
3. For "Monitortyp" select "HTTP(s)"
4. For the "URL" http://SWAP_WITH_YOUR_LXC_IP_ADRESS:8788/health
5. Safe

##
I hope you like this! This is my first repo, so will to give me advice!
You can ask my questions in german too!






