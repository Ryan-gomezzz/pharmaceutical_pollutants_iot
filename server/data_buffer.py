class DataBuffer:
    def __init__(self, size=10):
        self.size = size
        self.buffer = []
        
    def append(self, reading):
        self.buffer.append(reading)
        if len(self.buffer) > self.size:
            self.buffer.pop(0)
            
    def get_buffer(self):
        return self.buffer

    def is_full(self):
        return len(self.buffer) == self.size
