#!/usr/bin/env bash

# Install Nginx if not already installed
if ! command -v nginx &> /dev/null; then
    sudo apt-get update
    sudo apt-get -y install nginx
fi

# Create necessary directories only if they don't exist
sudo mkdir -p /data/web_static/releases/test /data/web_static/shared

# Create a fake HTML file for testing Nginx configuration if not already present
if [ ! -e /data/web_static/releases/test/index.html ]; then
    echo "<html>
  <head>
  </head>
  <body>
    Holberton School
  </body>
</html>" | sudo tee /data/web_static/releases/test/index.html > /dev/null
fi

# Remove /data/web_static/current if it exists
if [ -L /data/web_static/current ]; then
    sudo unlink /data/web_static/current
fi

# Remove /data/web_static/current/index.html if it exists
if [ -f /data/web_static/current/index.html ]; then
    sudo rm /data/web_static/current/index.html
fi

# Create symbolic link pointing to the directory, not the file
sudo ln -s /data/web_static/releases/test /data/web_static/current

# Set ownership to the ubuntu user and group recursively
sudo chown -R ubuntu:ubuntu /data/

# Update Nginx configuration if not already configured
if ! grep -q '/hbnb_static/' /etc/nginx/sites-available/default; then
    config_block="\\\n\tlocation /hbnb_static/ {\n\t\talias /data/web_static/current/;\n\t}\n"
    sudo sed -i "/^http {/a $config_block" /etc/nginx/sites-available/default

    # Restart Nginx
    sudo systemctl restart nginx
fi

# Exit successfully
exit 0

