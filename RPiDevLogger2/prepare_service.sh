#!/bin/bash

##################################################
# create application startup script

echo 'Create application startup script'

#cd ./SmartCrane/ParameterRecorder

if [ -f "start.sh" ]
then rm start.sh
fi

echo '#!/bin/bash' >> start.sh

echo 'python3 main.py' >> start.sh

chmod u+x start.sh

##################################################
# Initialize parameter_recorder.service

if [ -f "/etc/systemd/system/rpi_dev_logger2.service" ]
then rm /etc/systemd/system/rpi_dev_logger2.service
fi

echo '[Unit]' >> /etc/systemd/system/rpi_dev_logger2.service
echo 'Description=RPiDevLogger2 service' >> /etc/systemd/system/rpi_dev_logger2.service
echo '' >> /etc/systemd/system/rpi_dev_logger2.service
echo '[Service]' >> /etc/systemd/system/rpi_dev_logger2.service
echo 'Type=simple' >> /etc/systemd/system/rpi_dev_logger2.service
echo 'WorkingDirectory=/home/pi/RPiDevLogger2' >> /etc/systemd/system/rpi_dev_logger2.service
echo 'ExecStart=/home/pi/RPiDevLogger2/start.sh' >> /etc/systemd/system/rpi_dev_logger2.service
echo '' >> /etc/systemd/system/rpi_dev_logger2.service
echo '[Install]' >> /etc/systemd/system/rpi_dev_logger2.service
echo 'WantedBy=multi-user.target' >> /etc/systemd/system/rpi_dev_logger2.service

systemctl daemon-reload
systemctl enable rpi_dev_logger2
