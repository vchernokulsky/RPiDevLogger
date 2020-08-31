import json
import shutil


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
    key = "frequency"
    ret = None
    try:
        with open('config.json') as f:
            j_dict = json.load(f)
            if j_dict is not None and key in j_dict:
                ret = j_dict[key]
    except Exception as e:
        print(e)
    return ret


def config_validate(frequency):
    ret = None
    if frequency is None:
        print("couldn't read frequency from configuration file")
        return ret
    try:
        ret = float(frequency)
    except Exception as e:
        print(e)
    finally:
        return ret


def main():
    if not memory_enough():
        print("not enough free space")
    freq = config_validate(read_config())
    if freq is None:
        print("FAILED")
        return
    print("Frequecy: %f" % freq)


if __name__ == "__main__":
    main()
