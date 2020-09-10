class FileListWriter:
    def __init__(self, file_list):
        self.file_list = file_list
        self.writer_list = []

    def create_list(self):
        for name in self.file_list:
            f = open(name, 'w')
            self.writer_list.append(f)
        return len(self.writer_list)

    def write(self, data):
        for w in self.writer_list:
            w.write(data)

    def close(self):
        for w in self.writer_list:
            w.close()
