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

if [ -f "/etc/systemd/system/rpi_dev_logger.service" ]
then rm /etc/systemd/system/rpi_dev_logger.service
fi

echo '[Unit]' >> /etc/systemd/system/rpi_dev_logger.service
echo 'Description=RPiDevLogger service' >> /etc/systemd/system/rpi_dev_logger.service
echo '' >> /etc/systemd/system/rpi_dev_logger.service
echo '[Service]' >> /etc/systemd/system/rpi_dev_logger.service
echo 'Type=simple' >> /etc/systemd/system/rpi_dev_logger.service
echo 'WorkingDirectory=/home/pi/RPiDevLogger' >> /etc/systemd/system/rpi_dev_logger.service
echo 'ExecStart=/home/pi/RPiDevLogger/start.sh' >> /etc/systemd/system/rpi_dev_logger.service
echo '' >> /etc/systemd/system/rpi_dev_logger.service
echo '[Install]' >> /etc/systemd/system/rpi_dev_logger.service
echo 'WantedBy=multi-user.target' >> /etc/systemd/system/rpi_dev_logger.service

systemctl daemon-reload
systemctl enable rpi_dev_logger
sleep 2
systemctl start rpi_dev_logger