########################################################################
# Red-black Tree Data Structure
########################################################################

from simplelist import SimpleStruct
from trees import BinaryNode, Tree
from sys import exc_info

class RBTree(Tree):
    def __init__(self, Tree):
        Tree.__init__(self, SimpleStruct)
        self.type = "RBTree"
    
    
    def black_contingency(self, child):
        pass
    
    
    def red_contingency(self, child):
        """Resolves a potential double red case.
        This method houses both the code for recoloring
        and restructuring based on the situation.
        """
        parent = child.parent
        if parent is None:
            child.red = False
            return
        elif not parent.red:
            # If it is not really a double red situation...
            return
        
        grand = parent.parent
        # There will never be a double red situation where no gp exists
        # because the root is always black.
        rightchild = parent.right == child # Determine path of c-p-gp
        rightparent = grand.right == parent
        uncle = grand.left if rightparent else grand.right
        
        # Check uncle color for what to do
        if not uncle is None and uncle.red:
            # Uncle must exist to be red.
            uncle.red = False
            parent.red = False
            grand.red = True
            self.red_contingency(grand)
        else: # If the uncle is null/black...
            # Perform restructuring on double red. Terminal.
            ancestor = grand.parent
            rightgrand = ancestor is not None and ancestor.right == grand
            if self.root == grand:
                self.root = parent if rightchild == rightparent else child
            # In all 4 restructuring cases, gb turns red.
            grand.red = True
            
            if not rightchild and not rightparent:
                parent.red = False
                grand = self.rotate_left(grand)
            elif rightchild and not rightparent:
                child.red = False
                grand.left = self.rotate_right(parent)
                grand = self.rotate_left(grand)
            elif not rightchild and rightparent:
                child.red = False
                grand.right = self.rotate_left(parent)
                grand = self.rotate_right(grand)
            else:
                parent.red = False
                grand = self.rotate_right(grand)
            
            # If the gp node is not the root, reconnect the subtree to the
            # rest of the tree.
            if ancestor is not None:
                if rightgrand:
                    ancestor.right = grand
                else:
                    ancestor.left = grand
    
    
    def binary_insert(self, prev, cur, element):
        if cur is None:
            newnode = BinaryNode(element)
            if prev is None:
                newnode.red = False
                self.root = newnode
            else:
                newnode.parent = prev
                newnode.depth = prev.depth + 1
                self.max_depth = max(newnode.depth, self.max_depth)
                if element - prev.value > 0:
                    prev.right = newnode
                else:
                    prev.left = newnode
                try:
                    self.red_contingency(newnode)
                except:
                    e = exc_info()
                    for a in e:
                        print(a)
            return True
        comparison = element - cur.value
        
        # if comparison == 0:
            # return False
        if comparison > 0:
            return self.binary_insert(cur, cur.right, element)
        else:
            return self.binary_insert(cur, cur.left, element)
    
    
    def insert(self, element):
        if self.size == self.max_elements:
            return "Too many elements!"
        elif element > 99:
            return "Elements for Red-black Tree need to be 0 to 99 inclusive..."
        success = self.binary_insert(None, self.root, element)
        return str(element) + " inserted." if success else "I couldn't insert " + str(element) + "..."

