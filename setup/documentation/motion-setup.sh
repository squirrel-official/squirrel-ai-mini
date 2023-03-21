sudo chmod -R 777 /var/log/
#Install Motion
sudo apt-get install motion -y

#Update motion permissions
chmod -R 777 /var/log/motion
chmod -R 777 /var/lib/motion
sudo chmod -R 777 /etc/motion
sudo chmod -R 777 /usr/local/squirrel-ai/

#enable Motion on reboot
sudo systemctl enable motion


#add following using
sudo visudo

root  ALL=(ALL:ALL) NOPASSWD: /usr/local/squirrel-ai/motion-restart.sh
pi  ALL=(ALL:ALL) NOPASSWD: /usr/sbin/service  motion stop
pi  ALL=(ALL:ALL) NOPASSWD: /usr/sbin/service  motion start

crontab -e
@reboot sh /usr/local/squirrel-ai/motion-restart.sh




