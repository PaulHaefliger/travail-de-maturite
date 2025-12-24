#! /bin/bash

IS_ACTIVE=$(sudo systemctl is-active raspberrypaul)
if [ "$IS_ACTIVE" == "active" ]; then
    sudo systemctl restart raspberrypaul
else
    sudo cat > /etc/systemd/system/raspberrypaul.service << EOF
[Unit]
Description=RaspberryPaul
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=paul
WorkingDirectory=/home/paul
ExecStart=/home/paul/Documents/paul-tm/raspberrypi/run.sh

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl enable raspberrypaul.service
    sudo systemctl start raspberrypaul.service
fi

exit 0