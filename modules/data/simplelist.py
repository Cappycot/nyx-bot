import asyncio

def render(element):
    if element < 10:
        return "00" + str(element)
    elif element < 100:
        return "0" + str(element)
    return str(element)


class SimpleStruct:
    def __init__(self):
        self.data = []
        self.max_elements = 40
        self.size = 0
        self.type = "Basic ArrayList"
    
    def insert(self, element):
        if self.size == self.max_elements:
            return False
        self.data.append(element)
        self.size += 1
        return True
    
    def remove(self, element):
        try:
            self.data.remove(element)
            self.size -= 1
            return str(element) + " removed."
        except:
            return "I couldn't remove " + str(element) + "..."
    
    def output(self):
        return str(self.data)
        
