# A simple Etsy Oauth2.0 Integration
## 1. Introduction
This is a simple Etsy Oauth2.0 integration solution on Djagno framework.

## 2. Technical Stacks
- [DRF](https://www.django-rest-framework.org/)
- [AWS](https://aws.amazon.com)
- [Oauth2](https://www.rfc-editor.org/rfc/rfc6749)

## How to deploy in production
### Prerequests
- OS: Ubuntu 22.04
### Steps
1. Install dependency packages
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install apache2 libapache2-mod-wsgi-py3
```
2. Clone the project. (assuming it is cloned in `/home/ubuntu/EtsyOauth2/`) and move to the project directory.
3. Install project dependency libraries.
```
sudo pip3 install -r requirements.txt
```
4. Grant full permission to the project.
```
sudo chmod 777 ./
```
5. Write `.env` file in the project directory. Make sure to give proper permission to the log path configured in the environment.
6. Migrate database.
```
python3 manage.py migrate
```
7. Collect static files.
```
python3 manage.py collectstatic
```
8. Update `/etc/apache2/sites-available/000-default.conf` with the following contents.
```
<VirtualHost *:80>

	ServerName <Server IP>
	ServerAdmin webmaster@localhost
	DocumentRoot /home/ubuntu/EtsyOauth2

	<Directory "/home/ubuntu/EtsyOauth2">
		Require all granted
	</Directory>

	Alias /static/ "/home/ubuntu/EtsyOauth2/static/"
	<Directory "/home/ubuntu/EtsyOauth2/static">
		Require all granted
	</Directory>

	<Directory /home/ubuntu/EtsyOauth2/config>
		<Files wsgi.py>
			Require all granted
		</Files>
	</Directory>

	WSGIDaemonProcess etsyoauth2 python-path=/home/ubuntu/EtsyOauth2/:/usr/local/lib/python3.10/dist-packages
	WSGIProcessGroup etsyoauth2
	WSGIApplicationGroup %{GLOBAL}
	WSGIScriptAlias / /home/ubuntu/EtsyOauth2/config/wsgi.py	

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>
```
9. Restart apache service and check if the app is running in the 80 port.
```
sudo systemctl restart apache2
```
10. Install [certbot](https://certbot.eff.org/) dependencies to setup https.
```
sudo apt-get install certbot
sudo apt-get install python3-certbot-apache
```
11. Comment the following `wsgi` related contents from the `000-default.conf` and update server name to the domain.
```
WSGIDaemonProcess etsyoauth2 python-path=/home/ubuntu/EtsyOauth2/:/usr/local/lib/python3.10/dist-packages
WSGIProcessGroup etsyoauth2
WSGIApplicationGroup %{GLOBAL}
WSGIScriptAlias / /home/ubuntu/EtsyOauth2/config/wsgi.py	
```
12. Issue certificate with certbot.
```
sudo certbot --apache -d oauth2login.com
```
13. Uncomment the above `wsgi` related contents from the `000-default-le-ssl.conf` file which is created by certbot.
14. Restart apache service and access to the app with https.
```
sudo systemctl restart apache2
```