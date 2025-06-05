class ini:
    def __init__(self,filename):
        self.data = {}
        with open(filename,'r') as infile:
            for line in infile:
                index = line.find('#')
                if index > 0:
                    line = line[:index]
                else:
                    line = line[:-1]
                line = line.split('=')
                if len(line) !=2:
                    continue
                self.data[line[0]] = line[1]

    def __getitem__(self,key):
        return self.data[key]
