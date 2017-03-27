########################################################################
# Standard Max Heap
########################################################################

from simplelist import SimpleStruct, render
from sys import exc_info

class MaxHeap(SimpleStruct):
    def __init__(self, SimpleStruct):
        SimpleStruct.__init__(self)
        self.type = "Max Heap"
        self.data = [None] # Too lazy to make first pos 0
    
    
    def percolate_down(self, pos):
        temp = self.data[pos]
        while pos * 2 <= self.size:
            # print("move down to " + str(pos * 2))
            newpos = pos * 2
            less1 = temp < self.data[newpos]
            less2 = newpos + 1 <= self.size and temp < self.data[newpos + 1]
            if less2 and less1:
                less1 = self.data[newpos] > self.data[newpos + 1]
                less2 = not less1
            if less1:
                self.data[pos] = self.data[newpos]
            elif less2:
                newpos += 1
                self.data[pos] = self.data[newpos]
            else:
                break
            pos = newpos
        self.data[pos] = temp
    
    
    def percolate_up(self, pos):
        temp = self.data[pos]
        while int(pos / 2) >= 1:
            # print("move up to " + str(int(pos / 2)))
            newpos = int(pos / 2)
            if temp > self.data[newpos]:
                self.data[pos] = self.data[newpos]
            else:
                break
            pos = newpos
        self.data[pos] = temp
    
    
    def heapify(self):
        """Also known as buildheap."""
        # self.size = len(self.data) - 1
        for i in range(int(self.size / 2), 0, -1):
            # print("Percolating " + str(i) + "...")
            self.percolate_down(i)
    
    
    def insert(self, element):
        if self.size == self.max_elements:
            return False
        self.data.append(element)
        self.size += 1
        self.percolate_up(self.size)
        return True
    
    
    def delete_min(self):
        if self.size < 1:
            return None
        removed = self.data[pos]
        self.data[1] = self.data[self.size]
        self.size -= 1
        percolate_down(1)
        return removed
    
    
        
