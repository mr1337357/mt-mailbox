class mqueue:
    def __init__(self):
        self.messages = []
        self.index = 0

    def send(self,src,date,message):
        self.messages.append((src,date,message))

    def get(self,index=0):
        if index > 0:
            self.index = index - 1
        if self.index >= len(self.messages):
            self.index = 0
            return 'no more messages'
        else:
            msg = self.messages[self.index]
            self.index += 1
            return '{} of {} {}: {}'.format(self.index,len(self.messages),msg[0],msg[2])

    def delete(self,index=0):
        index -= 1
        if index < 0:
            index = 0
        print('delete {}'.format(index))
        if index < len(self.messages):
            del self.messages[index]
    
    def clean(self,date):
             pass
