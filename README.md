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

That's it, enjoy!
