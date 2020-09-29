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

# Декодеры

## samples512hz

### Описание

Декодер, используемый в RPiDevLogger.

Сокращает частоту поступающего сигнала до 512Hz. 0-ой канал – младший бит; 11-ый старший.
В выходном файле: в16-битном слове 4 старших бита (12-15) добиваются нулями.

![status output](/doc/decoder2.png)

### Установка

Для установки декодера необходимо скопировать папку `samples512hz`  в `/usr/share/libsigrokdecode/decoders/`.

Команда копирования:
`sudo cp -r samples512hz /usr/share/libsigrokdecode/decoders/`

## LogicFilter

### Описание

Отсеивает данные, оставляя только те, что соответствуют середине положительной площадки по Clock каналу.

![status output](/doc/decoder1.jpeg)

### Установка

Для установки декодера необходимо скопировать папку `LogicFilter`  в `/usr/share/libsigrokdecode/decoders/`.

Команда копирования:
`sudo cp -r LogicFilter /usr/share/libsigrokdecode/decoders/`

# Драйвера

Для работы с устройством saleae-logic-16 необходимо установить соответствующие драйвера (https://sigrok.org/wiki/Saleae_Logic16).

Для этого из папки `drivers` необходимо выполнить следующую команду:` sudo cp saleae-logic* /usr/share/sigrok-firmware/`

# Декодирование файла .logicdata

* Преобразование logicdata в bin

Для этого в SaleaeLogicSoftware открыть файл _.logicdata_ и нажать _Options > Export Data > Export_

![status output](/doc/saleae_logic_software.png)

* Декодирование в текстовый формат

`sigrok-cli -i filename.bin -I binary:numchannels=16:samplerate=500000 --config samplerate=500k -P samples512hz > decoded_filename.log` ,

где _filename_ - имя файла, полученного в пункте 1,

_decoded_filename_ - имя файла, в который будут записаны результаты декодирования. 

* Декодирование в бинарный формат

`sigrok-cli -i filename.bin -I binary:numchannels=16:samplerate=500000 --config samplerate=500k -P samples512hz -B samples512hz > decoded_filename.bin` ,

где _filename_ - имя файла, полученного в пункте 1,

_decoded_filename_ - имя файла, в который будут записаны результаты декодирования. 

