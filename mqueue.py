import time

SECONDS_PER_DAY = 86400

class mqueue:
    def __init__(self):
        self.messages = []
        self.index = 0
        self.index2 = 0

    def send(self,src,date,message):
        if date == 0:
            date = int(time.time())
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
    
    def clean(self):
        if len(self.messages) == 0:
            return
        now = time.time()
        past = now - ( 5 * SECONDS_PER_DAY)
        if self.index2 >= len(self.messages):
            self.index2 = 0

        message = self.messages[self.index2]
        if message[1] < past:
            self.messages.remove(message)
        self.index += 1

    def __len__(self):
        return len(self.messages)
