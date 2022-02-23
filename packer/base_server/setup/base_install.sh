apt-get update
apt-get upgrade -y
apt-get install -y nginx docker certbot

# Setup Weekly Security Updates
mv /tmp/weekly_update.sh /etc/cron.weekly/
chmod 755 /etc/cron.weekly/weekly_update.sh
