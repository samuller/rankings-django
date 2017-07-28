# Remove pre-installed software from Ubuntu Server
sudo apt-get remove apache2* rpcbind bind9

# Update server to newest state
sudo apt-get update
sudo apt-get upgrade

# Set timezone to UTC (use `sudo dpkg-reconfigure tzdata` to do it manually)
sudo apt-get install systemd-services
timedatectl set-timezone UTC
timedatectl set-ntp true

# Install basics for any Ubuntu
sudo apt-get install nano tmux htop nmap apt-transport-https

# Install software required by our app
sudo apt-get install git python-pip python-virtualenv sqlite3

# Install a version of nginx that is newer than currently in the repositories
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:nginx/stable
sudo apt-get update
sudo apt-get install nginx

# Globally install gunicorn
sudo pip install gunicorn

ssh-keygen
