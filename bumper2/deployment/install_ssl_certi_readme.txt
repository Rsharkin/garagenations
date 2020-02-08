
Using:
https://letsencrypt.org/

A tiny script to issue and renew TLS certs from Let's Encrypt:
https://github.com/diafygi/acme-tiny

Step 1: Create a Let's Encrypt account private key
openssl genrsa 4096 > account.key

Step 2: Create a certificate signing request (CSR) for your domains.
#generate a domain private key
openssl genrsa 4096 > domain.key

#for a single domain
openssl req -new -sha256 -key domain.key -subj "/CN=bumper.com" > domain.csr

#for multiple domains (use this one if you want both www.yoursite.com and yoursite.com)
openssl req -new -sha256 -key domain.key -subj "/" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:bumper.com,DNS:www.bumper.com")) > domain.csr

Step 3: Make your website host challenge files
#make some challenge folder (modify to suit your needs)
mkdir -p /var/www/challenges/

#example for nginx
server {
    listen 80;
    server_name yoursite.com www.yoursite.com;

    location /.well-known/acme-challenge/ {
        alias /var/www/challenges/;
        try_files $uri =404;
    }

    ...the rest of your config
}

Step 4: Get a signed certificate!
#run the script on your server
python acme-tiny/acme_tiny.py --account-key ./account.key --csr ./domain.csr --acme-dir /var/www/challenges/ > ./signed.crt

Step 5: Install the certificate
#NOTE: For nginx, you need to append the Let's Encrypt intermediate cert to your cert
wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
cat signed.crt intermediate.pem > chained.pem


Step 6: Create Cron file.

#!/usr/bin/sh
python /home/ubuntu/ssl/acme-tiny/acme_tiny.py --account-key /home/ubuntu/ssl/account.key --csr /home/ubuntu/ssl/domain.csr --acme-dir /var/www/challenges/ > /tmp/signed.crt || exit
wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
cat /tmp/signed.crt intermediate.pem > /home/ubuntu/ssl/chained.pem
service nginx reload
