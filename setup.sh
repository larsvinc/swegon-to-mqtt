#!/bin/sh
USER=pi
TITLE="Swegon Casa modbus daemon."


WORKINGDIR=`pwd`
DAEMON=`basename "$PWD"`
EXECUTE="/usr/bin/python3 $WORKINGDIR/$DAEMON.py"

# Add daemon user
sudo adduser --system --no-create-home --group $USER

# Add python packages
sudo apt install python3-pip
sudo pip3 install simplemodbus paho-mqtt


# Systemd integration. Use template to create appropriate config file
SERVICEFILE="$WORKINGDIR/systemd/$DAEMON.service"
sudo cp $WORKINGDIR/systemd/template.service $SERVICEFILE
sudo sed -i s/"TITLE"/"$TITLE"/g $SERVICEFILE
sudo sed -i s/"USER"/$USER/g $SERVICEFILE
sudo sed -i s@"WORKINGDIR"@"$WORKINGDIR"@g $SERVICEFILE
sudo sed -i s@"EXECUTE"@"$EXECUTE"@g $SERVICEFILE

sudo ln -s $WORKINGDIR/systemd/$DAEMON.service /etc/systemd/system/multi-user.target.wants/$DAEMON.service
sudo systemctl daemon-reload


# Setup log and logrotate integration
sudo mkdir /var/log/$DAEMON/
sudo chown $USER:$USER /var/log/$DAEMON/
LOGROTATEFILE="$WORKINGDIR/logrotate/$DAEMON"
LOGFILE="/var/log/$DAEMON/$DAEMON.log"

sudo cp $WORKINGDIR/logrotate/template $LOGROTATEFILE
sudo sed -i s@"LOGFILE"@$LOGFILE@g $SERVICEFILE

sudo cp $LOGROTATEFILE /etc/logrotate.d/
echo "Please make sure that program logs to:"
echo $LOGFILE
