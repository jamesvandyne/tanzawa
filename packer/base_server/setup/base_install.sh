# Install nginx and base packages required to install Docker

apt-get update && apt-get install -y apt-utils nginx certbot apt-transport-https ca-certificates curl gnupg lsb-release python3-pip

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker Repo
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \

apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io && apt-get upgrade -y

# Docker compose
pip3 install docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
mv /tmp/docker-compose.yml /opt/tanzawa/

# Setup Weekly Security Updates
mv /tmp/weekly_update.sh /etc/cron.weekly/
chmod 755 /etc/cron.weekly/weekly_update.sh


mkdir -p /etc/nginx/sites-available/ /etc/nginx/sites-enabled
# Move nginx config files into location
cp /tmp/uwsgi_params /etc/nginx/uwsgi_params
cp /tmp/nginx.conf /etc/nginx/sites-available/tanzawa.conf
ln -s /etc/nginx/sites-available/tanzawa.conf /etc/nginx/sites-enabled/
unlink /etc/nginx/sites-enabled/default