import json
import shutil

from file_manager import FileManager

CONFIG_FILE = 'config.json'

FREQ = 0
MIN_MEM_FREE = 1
RM_KOEF = 2

keys = ['frequency', 'min_free_space_gb', 'file_remove_koef']


def memory_enough():
    total, used, free = shutil.disk_usage("/")

    print("Total: %d GiB" % (total // (2 ** 30)))
    print("Used: %d GiB" % (used // (2 ** 30)))
    print("Free: %d GiB" % (free // (2 ** 30)))

    if free < 1:
        return False
    else:
        return True


def read_config():
    j_dict = None
    try:
        with open(CONFIG_FILE) as f:
            j_dict = json.load(f)
    except Exception as e:
        print(e)
    return j_dict


def format_config(j_dict):
    params = {}
    if j_dict is None:
        print("fail to read configuration file")
        return None
    for key in keys:
        if key not in j_dict:
            print('key "{}" missed in configuration file'.format(key))
            return None
        val = validate_value(j_dict[key])
        if val is None:
            print('{} value couldn\'t be converted to float'.format(key))
            return None
        params[key] = val
    return params


def validate_value(val):
    ret = None
    try:
        ret = float(val)
    except Exception as e:
        print(e)
    finally:
        return ret


def main():
    config = format_config(read_config())
    if config is None:
        return
    print("configuration: {}".format(config))

    fm = FileManager(config[keys[MIN_MEM_FREE]], config[keys[RM_KOEF]])
    if not fm.check_folders():
        return

    if not fm.check_memory():
        return


if __name__ == "__main__":
    main()
