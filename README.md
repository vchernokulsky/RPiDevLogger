# RPiDevLogger

## Установка и создание сервиса

- разместите RPiDevLogger в директории `/home/pi`
- перейдите в RPiDevLogger
- настройте права доступа для скрипта `chmod u+x prepare_service.sh`
- запустите скрипт `sudo ./prepare_service.sh`
- проверьте, что сервис создался: `systemctl status rpi_dev_logger.service`

примерный вывод команды, если сервис был успешно создан

![status output](/doc/status.png)

- запустите сервис `sudo systemctl start rpi_dev_logger.service`


## Основные настройки(_config.json_)
пример файла: 

`{
  "frequency": 100.0,
  "min_free_space_gb": 1.0,
  "file_remove_koef": 5.0
}`

_frequency_ - частота дискретезации сигнала, поступаюшего с saleae logic

_min_free_space_gb_ - (_Limit_) -  минимальный объём свободной памяти на диске, необходимый для работы RPiDevLogger(в Гб)

_file_remove_koef_ - (_K_) - коэффициент освобождения памяти

Если при запуске **RPiDevLogger** объем свободной памяти(_Free_mem_) меньше минимально необходимой (_Free_mem < Limit_), 
то программа пытается высвободить объем памяти равный _K * Limit_, удалив файлы сохраненных сессий с наименьшими номерами.
