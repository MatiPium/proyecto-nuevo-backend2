cat > .env << 'EOF'
DJANGO_SECRET_KEY=dev-unsafe-key
DJANGO_DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=sqlite
DB_NAME=db.sqlite3
EOF

