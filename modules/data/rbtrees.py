########################################################################
# Red-black Tree Data Structure
########################################################################

from simplelist import SimpleStruct
from trees import BinaryNode, Tree
from sys import exc_info

class RBTree(Tree):
    def __init__(self, Tree):
        Tree.__init__(self, SimpleStruct)
        self.type = "Red-black Tree"
    
    
    def black_contingency(self, child):
        """Resolves a double black situation..."""
        # print("DB at element " + str(child.value) + "...")
        parent = child.parent
        # Case 0: The DB node is actually root and no one cares...
        if parent is None:
            return
        
        # Get conditions for cases...
        rightchild = parent.right == child
        sibling = parent.left if rightchild else parent.right
        leftred = sibling.left is not None and sibling.left.red
        rightred = sibling.right is not None and sibling.right.red
        # Since rotations detach the subtree from the ancestor,
        # the ancestor node is needed just in case.
        grand = parent.parent
        rightparent = grand is not None and grand.right == parent
        # What will be the highest node in the subtree?
        connectup = sibling
        
        # If the sibling is black: Perform a restructuring if we can
        # find a red child of the sibling.
        if not sibling.red:
            # Case 1: The sibling is black with a red child...
            if leftred or rightred:
                # print("Case 1")
                # If the red sibling child is closer to the DB node
                # then double rotate the sibling child to parent
                # and set that as the node to connect to ancestor.
                if leftred and not rightchild:
                    sibling.left.red = parent.red
                    parent.right = self.rotate_left(sibling)
                    # Lesson learned is that ancestors always need to be
                    # reconnected after every rotation if like this...
                    connectup = self.rotate_right(parent)
                elif rightred and rightchild:
                    sibling.right.red = parent.red
                    parent.left = self.rotate_right(sibling)
                    connectup = self.rotate_left(parent)
                # If the red sibling child is farther from the DB node
                # then single rotate the sibling to parent.
                elif leftred and rightchild:
                    sibling.red = parent.red
                    sibling.left.red = False
                    self.rotate_left(parent)
                else:
                    sibling.red = parent.red
                    sibling.right.red = False
                    self.rotate_right(parent)
                parent.red = False
                if grand is not None:
                    if rightparent:
                        grand.right = connectup
                    else:
                        grand.left = connectup
            # Case 2: The sibling has no red child...
            elif parent.red:
                # If the parent is red, we can stop here
                # with a simple color swap.
                sibling.red = True
                parent.red = False
            else:
                # print("Case 2")
                # The sibling is colored red to balance with the DB
                # node, but the problem propagates upward...
                sibling.red = True
                # print(self.output())
                self.black_contingency(parent)
        # Case 3: The sibling is red...
        else:
            # print("Case 3")
            # Single rotate sibling up to parent and reconnect to
            # ancestor. Then the DB problem propagates upward.
            if rightchild:
                self.rotate_left(parent)
            else:
                self.rotate_right(parent)
            parent.red = True
            sibling.red = False
            if grand is not None:
                if rightparent:
                    grand.right = connectup
                else:
                    grand.left = connectup
            # print(self.output())
            self.black_contingency(child)
    
    
    def remove(self, element):
        to_delete = self.delete(self.root, element)
        if to_delete is None:
            return "I couldn't find " + str(element) + "..."
        if not to_delete.red:
            self.black_contingency(to_delete)
        self.detach(to_delete)
        self.size -= 1
        return str(element) + " removed."
    
    
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
            # if self.root == grand:
                # self.root = parent if rightchild == rightparent else child
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
                self.red_contingency(newnode)
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
            return False
        elif element > 99:
            return False
        self.size += 1
        success = self.binary_insert(None, self.root, element)
        return success

