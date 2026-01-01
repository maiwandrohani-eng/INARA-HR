#!/bin/bash

# SSL Certificate Setup Script using Let's Encrypt
# Run this script to set up SSL certificates for your domain

set -e

DOMAIN="${1:-your-domain.com}"
EMAIL="${2:-admin@${DOMAIN}}"

if [ "$DOMAIN" == "your-domain.com" ]; then
    echo "Usage: ./ssl-setup.sh <your-domain.com> <your-email@example.com>"
    exit 1
fi

echo "Setting up SSL certificates for ${DOMAIN}..."
echo "Email: ${EMAIL}"

# Install certbot if not installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y certbot
    elif command -v yum &> /dev/null; then
        sudo yum install -y certbot
    else
        echo "Please install certbot manually"
        exit 1
    fi
fi

# Create directory for ACME challenge
sudo mkdir -p /var/www/certbot

# Obtain certificate
echo "Obtaining SSL certificate..."
sudo certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "${EMAIL}" \
    --agree-tos \
    --no-eff-email \
    -d "${DOMAIN}" \
    -d "www.${DOMAIN}"

# Create nginx SSL directory
sudo mkdir -p /etc/nginx/ssl

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /etc/nginx/ssl/
sudo cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem /etc/nginx/ssl/

# Set proper permissions
sudo chmod 600 /etc/nginx/ssl/privkey.pem
sudo chmod 644 /etc/nginx/ssl/fullchain.pem

echo "✅ SSL certificates installed!"
echo ""
echo "Next steps:"
echo "1. Update nginx.conf with your domain name"
echo "2. Update SSL certificate paths if needed"
echo "3. Restart nginx: sudo systemctl restart nginx"
echo ""
echo "To auto-renew certificates, add to crontab:"
echo "0 0 * * * certbot renew --quiet --deploy-hook 'systemctl reload nginx'"

