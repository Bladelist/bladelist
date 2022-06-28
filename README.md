<h1 align="center">Welcome to Bladelist 👋</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-2.0.0-blue.svg?cacheSeconds=2592000" />
  <a href="https://docs.bladebotlist.xyz" target="_blank">
    <img alt="Documentation" src="https://img.shields.io/badge/documentation-yes-brightgreen.svg" />
  </a>
  <a href="https://github.com/bladelist/bladelist/blob/master/LICENCE" target="_blank">
    <img alt="License: MIT LICENSE" src="https://img.shields.io/badge/License-MIT LICENSE-yellow.svg" />
  </a>
  <a href="https://discord.gg/WeUtJ7hqum" target="_blank">
    <img alt="Discord: Tortoise Community" src="https://img.shields.io/badge/Discord-Tortoise%20Community-%23ffb101" />
  </a>
  <a href="https://discord.gg/WeUtJ7hqum" target="_blank">
    <img alt="website" src="https://img.shields.io/website?url=https%3A%2F%2Fbladelist.gg" />
  </a>
</p>



> BladeList was built for users and developers to manage with ease thier bot page and create something clean.

## Setup instruction


#### You would need a linux system for development. Windows raises python-decouple errors. More info [here](https://github.com/bladelist/bladelist/issues/1).
#### You need Python 3.8 or above installed on your system.


### Development Setup
```bash
# Clone the repository or download as zip and cd into the root folder (bladelist)
# Terminal instructions (You're supposed run the below commands during the initial setup)

# Remove existing virtualenv module, We will let poetry install the required version
$ sudo apt-get remove virtualenv -y && sudo python3 -m pip uninstall virtualenv -y

# Install poetry
$ pip install poetry

# Install dependencies from poetry
$ poetry install

$ sudo nano .env
# add the following environment variables

DB_NAME = "your_db_name"
DB_HOST = "your_db_host"
DB_PASS = "your_db_password"
DB_USER = "your_db_user"

DEBUG = True

ENCRYPTION_SALT = "your_encryption_salt"
ENCRYPTION_ITERATION = your_iteration_count

AUTH_HANDLER_URL="http://localhost:8000/login/"
AUTH_CALLBACK_URL="http://localhost:8000login/handlers/"

OAUTH_CLIENT_ID = "your_client_id"
OAUTH_CLIENT_SECRET = "your_client_secret"
DISCORD_API_TOKEN="your_discord_api_token"
LOG_CHANNEL_ID="your_log_channel_id_here"

# Run the development server locally
$ poetry run python3 manage.py runserver 
# this should run the Django development server on your localhost:8000.
# now you can visit http://127.0.0.1:8000 and access the site.
```

### Adding host file configuration for subdomain access in development

### Production Setup

#### Addition Requirements:

[NGINX](https://nginx.org/en/): Webserver for handling requests and serving django assets.

[Supervisor](http://supervisord.org/): Process management tool for keeping Django running. It also provides logging in events of unaccounted crashes and restarts the application to keep it online.


#### Setup procedure for Ubuntu 20.04 LTS. This will also work for all Debian/Ubuntu based distros. Procedures for other distros maybe slightly different but follows almost the same flow.
```bash
# Clone the repository or download as zip and cd into the root folder (bladelist)

# Update and upgrade apt
$ sudo apt update && sudo apt upgrade -y

# If pip is not installed
$ sudo apt-get install python3-pip -y

# Remove virtualenv and let poetry install the required version
$ sudo apt-get remove virtualenv -y && sudo python3 -m pip uninstall virtualenv -y

# Clone the repository and cd into the folder
$ git clone https://github.com/bladelist/bladelist.git && cd bladelist

# Install poetry
$ sudo python3 -m pip install poetry

# Install dependencies from poetry
$ sudo poetry install

$ sudo nano .env
# add the following environment variables

DB_NAME = "your_db_name"
DB_HOST = "your_db_host"
DB_PASS = "your_db_password"
DB_USER = "your_db_user"

DEBUG = True

ENCRYPTION_SALT = "your_encryption_salt"
ENCRYPTION_ITERATION = your_iteration_count

AUTH_HANDLER_URL="https://bladelist.gg/login/"
AUTH_CALLBACK_URL="https://bladelist.gg/login/handlers/"

OAUTH_CLIENT_ID = "your_client_id"
OAUTH_CLIENT_SECRET = "your_client_secret"
DISCORD_API_TOKEN="your_discord_api_token"
LOG_CHANNEL_ID="your_log_channel_id_here"

# Run collectstatic to collect static files to assets folder for production
$ sudo poetry run python3 manage.py collectstatic

# install supervisord
$ sudo apt install supervisor -y

# install nginx
$ sudo apt install nginx -y
```
At this point, nginx should be running. 

If inbound connections are enabled for port 80, you'll be able to visit the ip with a browser which should give you the default NGINX landing page.

#### Supervisord configurations
add the below config inside `/etc/supervisor/conf.d/gunicorn.conf`
```shell
[program:gunicorn]
directory=/home/ubuntu/bladelist
command=poetry run python3 -m gunicorn --workers 3 --bind unix:/home/ubuntu/bladelist/app.sock core.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/gunicorn.err.log
stdout_logfile=/var/log/gunicorn/gunicorn.out.log

[group:guni]
programs:gunicorn
```

Make log and output files for supervisor
```bash
$ sudo mkdir /var/log/gunicorn && cd /var/log/gunicorn

$ sudo touch gunicorn.out.log
$ sudo touch gunicorn.err.log
```
Update supervisor to propagate changes

```bash
# Reread supervisor configurations
$ sudo supervisorctl reread

# Update supervisor configurations
$ sudo supervisorctl update

# Check if supervisor is correctly configured. 
$ sudo supervisorctl status
# If correctly configured the application should be running with pid and shows uptime. 
# Otherwise check the configurations or logs and try again.

# In case if supervisor status shows restarting, 
# 1) Check if gunicorn is installed 
# 2) check if the log and output files exist for supervisor
# 3) check the logs and check the Django application

# In case if supervisor status shows exited quickly
# 1) check if the directory and commands in the gunicorn.conf is correct
# 2) check the application, the environment variables, database.
```

#### NGINX Configurations

add the below config inside `/etc/nginx/sites-available/django.conf`

```shell
server {
        listen 80;
#        listen 443 ssl http2;
#        listen [::]:443 ssl http2;
#        ssl on;
#        ssl_certificate         /etc/ssl/certs/cert.pem;
#        ssl_certificate_key     /etc/ssl/private/key.pem;
#        ssl_client_certificate /etc/ssl/certs/cloudflare.crt;
#        ssl_verify_client on;

        server_name <ip_address_or_domain_here>;

        location / {
                include proxy_params;
                proxy_pass http://unix:/home/ubuntu/bladelist/app.sock;
        }
        location /static/ {
                autoindex on;
                alias /home/ubuntu/bladelist/assets/;
        }   
        location /protected/media/ {
                internal;
                alias /home/ubuntu/bladelist/media/;
        }
    
}
```
Once added, test if the configurations are okay and symlink with `sites-enabled`

```bash
$ sudo nginx -t
# If configurations are not okay, Check the nginx configuration again to see if paths added are correct

# If configurations shows okay, Symlink with sites-enabled
$ sudo ln  /etc/nginx/sites-available/django.conf /etc/nginx/sites-enabled

# Test nginx again
$ sudo nginx -t

# If configuration shows okay, Reload nginx
$ sudo systemctl reload nginx

# Reload supervisor
$ sudo systemctl reload supervisor
```

#### Once all the above setups are complete, we'll be able to visit the site in the domain/ip provided in the nginx configuration.