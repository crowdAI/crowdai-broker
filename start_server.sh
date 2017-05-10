

source env/bin/activate
gunicorn -k gevent -w 5  --bind 0.0.0.0:5001 wsgi:app
