import sys


class DataManager:
    def __init__(self):
        self.container = ""

    def append_data(self, data):
        self.container += data
        #print(data, end="")
    
    def present(self):
        #print("Data:")
        #print(self.container)
        sys.stdout.write("\033[92m%s\033[0m" % self.container[-1])
        sys.stdout.flush()

    def save_to_file(self, data_file):
        raise NotImplemented