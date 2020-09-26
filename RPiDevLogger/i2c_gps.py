import time
import json
import smbus
import logging

BUS = None
address = 0x42
gpsReadInterval = 0.1
LOG = logging.getLogger()

def connectBus():
    global BUS
    BUS = smbus.SMBus(1)


def parseResponse(gpsLine):
    global lastLocation
    gpsChars = ''.join(chr(c) for c in gpsLine)
    if "*" not in gpsChars:
        return False
    gpsParts = gpsChars.split('*')
    if len(gpsParts) != 2:
        print("cannot get checksum")
        return False
    gpsStr = gpsParts[0]
    chkSum = gpsParts[1]
    gpsComponents = gpsStr.split(',')
    gpsStart = gpsComponents[0]
    if gpsStart not in ["$GNRMC", "$GNGGA"]:
        return True
    if gpsStart == "$GNRMC":
        if len(gpsComponents) != 13:
            print("wrong fields number")
            return False
    if gpsStart == "$GNGGA":
        if len(gpsComponents) != 15:
            print("wrong fields number")
            return False
    chkVal = 0
    for ch in gpsStr[1:]:  # Remove the $
        chkVal ^= ord(ch)
    if chkVal != int(chkSum, 16):
        print("wrong checksum")
        return False
    print(gpsChars)
    return True


def readGPS():
    c = None
    response = []
    try:
        while True:  # Newline, or bad char.
            c = BUS.read_byte(address)
            if c == 255:
                return False
            elif c == 10:
                break
            else:
                response.append(c)
        parseResponse(response)
    except IOError:
        time.sleep(0.5)
        connectBus()
    except Exception as e:
        print(e)
        LOG.error(e)


connectBus()
while True:
    readGPS()
    time.sleep(gpsReadInterval)
