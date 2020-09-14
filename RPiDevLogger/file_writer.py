class FileListWriter:
    def __init__(self, file_list):
        self.file_list = file_list
        self.writer_list = []
        self.file_idx = 0

    def get_files_str(self):
        ret = ""
        if self.file_idx == 0:
            ret = " ".join(self.file_list)
        else:
            ret = " ".join([s + str(self.file_idx) for s in self.file_list])
        self.file_idx += 1
        return ret

    def create_list(self):
        for name in self.file_list:
            f = open(name, 'wb', buffering=0)
            self.writer_list.append(f)
        return len(self.writer_list)

    def write(self, data):
        for w in self.writer_list:
            w.write(data)

    def close(self):
        for w in self.writer_list:
            w.close()
