# Ubuntu Deployment

This is the first production-style deployment path for the MVP.

## Server Requirements

- Ubuntu Server 22.04 or newer
- Python 3.10+ recommended
- Git
- Nginx
- systemd

## Clone

```bash
cd /opt
sudo git clone https://github.com/tanalex0228-hash/mental-counseling-ai.git
sudo chown -R $USER:$USER /opt/mental-counseling-ai
cd /opt/mental-counseling-ai
```

## Python Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment

```bash
cp .env.example .env
nano .env
```

Required values:

```env
SECRET_KEY=change_this_to_a_long_random_secret
DEBUG=False
DJANGO_ALLOWED_HOSTS=your_domain.com,your_server_ip
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-mini
DATABASE_URL=sqlite:///db.sqlite3
```

## Database And Assets

```bash
python manage.py migrate
python manage.py seed_knowledge
python manage.py build_vector_index
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Gunicorn Test

```bash
.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

## systemd Service

Create:

```bash
sudo nano /etc/systemd/system/mental-counseling-ai.service
```

Content:

```ini
[Unit]
Description=Mental Counseling AI Django App
After=network.target

[Service]
User=YOUR_UBUNTU_USER
Group=www-data
WorkingDirectory=/opt/mental-counseling-ai
Environment="PATH=/opt/mental-counseling-ai/.venv/bin"
ExecStart=/opt/mental-counseling-ai/.venv/bin/gunicorn config.wsgi:application --workers 3 --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mental-counseling-ai
sudo systemctl start mental-counseling-ai
sudo systemctl status mental-counseling-ai
```

## Nginx

Create:

```bash
sudo nano /etc/nginx/sites-available/mental-counseling-ai
```

Content:

```nginx
server {
    listen 80;
    server_name your_domain.com your_server_ip;

    client_max_body_size 20M;

    location /static/ {
        alias /opt/mental-counseling-ai/staticfiles/;
    }

    location /media/ {
        alias /opt/mental-counseling-ai/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/mental-counseling-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## HTTPS

If you have a domain, use a public certificate:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

If you only have a public IP, use a temporary self-signed certificate. Browsers will show a warning, but traffic is encrypted:

```bash
sudo mkdir -p /etc/ssl/mental-counseling-ai
sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout /etc/ssl/mental-counseling-ai/selfsigned.key \
  -out /etc/ssl/mental-counseling-ai/selfsigned.crt \
  -subj "/CN=YOUR_PUBLIC_IP" \
  -addext "subjectAltName = IP:YOUR_PUBLIC_IP"
sudo chmod 600 /etc/ssl/mental-counseling-ai/selfsigned.key
```

Nginx HTTPS example:

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name YOUR_PUBLIC_IP;

    ssl_certificate /etc/ssl/mental-counseling-ai/selfsigned.crt;
    ssl_certificate_key /etc/ssl/mental-counseling-ai/selfsigned.key;

    client_max_body_size 25M;

    location /static/ {
        alias /home/alex/mental-counseling-ai/staticfiles/;
    }

    location /media/ {
        alias /home/alex/mental-counseling-ai/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

Set production HTTPS environment values:

```env
ENABLE_HTTPS=True
CSRF_TRUSTED_ORIGINS=https://YOUR_PUBLIC_IP
SECURE_HSTS_SECONDS=0
```

## Update Deployment

```bash
cd /opt/mental-counseling-ai
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_knowledge
python manage.py build_vector_index
python manage.py collectstatic --noinput
sudo systemctl restart mental-counseling-ai
```
