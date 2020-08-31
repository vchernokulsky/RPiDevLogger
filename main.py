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


def main():
    if not memory_enough():
        print("not enough free space")


if __name__ == "__main__":
    main()
