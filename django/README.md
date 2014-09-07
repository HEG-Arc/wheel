Django
======

Permission issues
-----------------

You have to add the `www-data` user to the following groups

 * dialout (to have access to the serial port in order to print tickets)
 * tty (to have access to the USB port)
 
Apache configuration
--------------------

Add the following lines to your Apache config (adapt the path):
```
        <Directory /home/wheel/wheel/django>
                Require all granted
        </Directory>
        Alias /wheel/assets /home/wheel/wheel/django/assets/
        WSGIDaemonProcess wheel processes=2 threads=15 display-name=%{GROUP} python-path=/home/wheel/wheel/django
        WSGIProcessGroup wheel
        WSGIScriptAlias / /home/wheel/wheel/django/wheel/wsgi.py
```

Static files
------------

Static files are served from the `assets` folder. In order to collect static files to the `assets` folder, run:

`./manage.py collectstatic --settings=wheel.settings.kiosk`

