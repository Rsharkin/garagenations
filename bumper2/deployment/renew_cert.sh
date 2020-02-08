#!/bin/bash
python /home/ubuntu/ssl/acme-tiny/acme_tiny.py --account-key /home/ubuntu/ssl/account.key --csr /home/ubuntu/ssl/domain.csr --acme-dir /var/www/challenges/ > /tmp/signed.crt || exit
wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
cat /tmp/signed.crt intermediate.pem > /home/ubuntu/ssl/chained.pem
service nginx reload