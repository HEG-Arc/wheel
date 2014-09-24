Wheel
=====

An interactive booth based on the wheel of fortune game

Chromium
--------

Wheel is best used with the Chromium browser (OK, uzbl is better, but not nicely starting in fullscreen mode).

To automate Chromium, you need Chromix (http://chromix.smblott.org/).

  * Install the chromi extension: https://chrome.google.com/webstore/detail/chromi/eeaebnaemaijhbdpnmfbdboenoomadbo
  * Install chromix-server: `sudo npm install -g chromix`
  * Run the chromix-server: `chromix-server`
  * Start chromium in fullscreen mode: `chromium-browser -start-fullscreen`
  * Open an URL in the current tab: `chromix with current goto http://localhost/booth/`

You need to create an init file to automate the startup of `chromix-server`

```
description "Chromix Server"
author "cedric.gaspoz@he-arc.ch"

start on runlevel [2345]
stop on runlevel [!2345]

respawn

exec /usr/bin/chromix-server
```

Mouse pointer
-------------

Fast and dirty trick to remove the mouse pointer from the screen (http://www.linuxquestions.org/questions/linux-general-1/manually-setting-x-cursor-or-theme-doesn%27t-work-no-errors-700965/#post3432670)

Download: http://downloads.yoctoproject.org/releases/matchbox/utils/xcursor-transparent-theme-0.1.1.tar.gz

```
./configure
cd cursors
make install-data-local DESTDIR=/home/wheel/.icons/default CURSOR_DIR=/cursors
chown -R wheel:wheel /home/wheel/.icons
```

Problem with the bumper
-----------------------

It seems that the Chromium window doesn't get the focus and is not responding to the <ENTER> key from the bumper. Use ``xdotool`` to send the <F5> key to Chromium.

```xdotool key --windowid "$(xdotool --search --class Chrome | head -n 1)" F5```

Also working:

```xdotool key F5```

Put it in the startup script (add ``sleep 30`` to wait until Chromium started)
