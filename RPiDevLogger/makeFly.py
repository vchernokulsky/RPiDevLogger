import os
import glob
import struct

DIR = '/home/pi/data1/'


def getFname():
    flist = glob.glob('/home/pi/data/*_logic.log')
    flist.sort()
    fname = flist[-2]
    return fname


def croplog(fname, fnum):
    with open(fname, mode='rb') as logic,\
            open(DIR+fnum+'_logic.crop', mode='wb') as crop:
        logic.seek(25600)
        again = True
        while again:
            words = logic.read(20)
            decimal = struct.unpack('10H', words)
            pos = decimal.index(1535)
            if decimal[pos + 1] == 1535:
                start = 25600+pos*2
                again = False
            else:
                continue
        logic.seek(start)
        for i in range(int((os.path.getsize(fname)-50000)/20)):
            tenwords = struct.unpack('10H', logic.read(20))
            if tenwords[0] == 1535 and tenwords[1] == 1535:
                crop.write(struct.pack('H', tenwords[6]))
            elif tenwords[0] != 1535 and tenwords[1] == 1535:
                logic.seek(-18, 1)
    return DIR+fnum+'_logic.crop'


def lineup(croped, fnum):
    with open(croped, mode='rb') as crop,\
            open(DIR+fnum+'_logic.log', mode='wb') as fly:
        first = struct.unpack('256H', crop.read(512))
        crop.seek(first.index(2559)*2)
        for i in range(int(os.path.getsize(croped)/512-1)):
            data = struct.unpack('256H', crop.read(512))
            if data[0] == 2559 and data[255] != 2559 and data[254] != 2559:
                fly.write(struct.pack('256H', *data))
            elif data[255] == 2559:
                fly.write(struct.pack('256H', *data))
                crop.seek(-2, 1)
            elif data[254] == 2559:
                fly.write(struct.pack('256H', *data))
                crop.seek(-4, 1)


def make_fly():
    fnum = getFname()[14:-10]
    lineup(croplog(getFname(), fnum), fnum)
    os.remove(DIR+fnum+'_logic.crop')
