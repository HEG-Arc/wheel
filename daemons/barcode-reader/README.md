Barcode-Reader
==============

This daemon read the barcode from the scanner and send the code to the browser / daemon

Run as daemon
-------------

To run as daemon, create a barcode-reader file in the /etc/init.d/ directory with the following code:

```
#!/bin/sh
DAEMON_NAME="barcode-reader"
DAEMON="/home/wheel/daemons/barcode-reader/barcode-reader.py"
mkdir -p /var/run/wheel
case "$1" in
  start)
    echo "Starting Barcode Reader"
    # Start the daemon
    python $DAEMON start
    ;;
  stop)
    echo "Stopping Barcode Reader"
    # Stop the daemon
    python $DAEMON stop
    ;;
  restart)
    echo "Restarting Barcode Reader"
    python $DAEMON restart
    ;;
  *)
    # Refuse to do other stuff
    echo "Usage: $DAEMON_NAME {start|stop|restart}"
    exit 1
    ;;
esac
exit 0
```

Then make it executable: `chmod +x /etc/init.d/barcode-reader`

Finally, run `update-rc.d barcode-reader defaults` in order to start the daemon during startup


