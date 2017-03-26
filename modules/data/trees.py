########################################################################
# Trees!
########################################################################

# ┌──┘ └──┐ └┘ ┴

from simplelist import SimpleStruct, render
from sys import exc_info


def rbrender(element, red):
    toreturn = str(element) + ("R" if red else "B")
    if element < 10:
        return "0" + toreturn
    return toreturn


class BinaryNode:
    def __init__(self, element):
        self.parent = None
        self.left = None
        self.right = None
        self.depth = 0
        self.red = True
        self.value = element


class Tree(SimpleStruct):
    def __init__(self, SimpleStruct):
        SimpleStruct.__init__(self)
        self.root = None
        self.max_depth = 0
    
    
    def rotate_left(self, parent):
        child = parent.left
        parent.left = child.right
        if not parent.left is None:
            parent.left.parent = parent
        child.parent = parent.parent
        parent.parent = child
        child.right = parent
        return child
        
    
    def rotate_right(self, parent):
        child = parent.right
        parent.right = child.left
        if not parent.right is None:
            parent.right.parent = parent
        child.parent = parent.parent
        parent.parent = child
        child.left = parent
        return child
            
    
    def restructure_data(self):
        for element in self.data:
            self.insert(element)
    
    
    def calc_depth(self, node, depth=0):
        """Preorder traversal to calculate the depths of all nodes."""
        if node is None:
            return True
        node.depth = depth
        noleft = self.calc_depth(node.left, depth + 1)
        noright = self.calc_depth(node.right, depth + 1)
        if noleft and noright:
            self.max_depth = max(depth, self.max_depth)
        return False
            
    
    def inorder(self, node, lines, leftchild, pos):
        if node is None:
            return -1
        
        # Ask how many nodes are to the left of this.
        leftpos = self.inorder(node.left, lines, True, pos)
        if leftpos == -1 and pos < 0:
            pos = 0 # The leftmost node because we didn't know our pos
        elif leftpos != -1:
            pos = leftpos + 1
            
        # print("There are " + str(pos) + " nodes to the left of " + str(node.value))
        # print(str(pos) + ": " + str(node.value) + " at depth " + str(node.depth))
        
        depth = node.depth
        linepos = pos * 3
        element = rbrender(node.value, node.red) if "RBTree" in self.type else render(node.value)
        
        # Add element to ASCII picture
        lengthen = linepos - len(lines[depth * 2])
        lines[depth * 2] += (" " * lengthen) + element
        
        linepos += 1
        
        # Upper branch connector
        if depth > 0:
            lengthen = linepos - len(lines[depth * 2 - 1])
            lengthchar = " " if leftchild else "─"
            lines[depth * 2 - 1] += (lengthchar * lengthen) + ("┌" if leftchild else "┐")
        
        # Lower branch connector
        if not node.left is None or not node.right is None:
            branchchar = "┴"
            if node.left is None:
                branchchar = "└"
            elif node.right is None:
                branchchar = "┘"
            lengthchar = "─" if not node.left is None else " "
            lengthen = linepos - len(lines[depth * 2 + 1])
            lines[depth * 2 + 1] += (lengthchar * lengthen) + branchchar
        
        rightpos = self.inorder(node.right, lines, False, pos + 1)
        return max(pos, rightpos)

        
    def output(self):
        """Output the tree in ASCII art form."""
        self.calc_depth(self.root)
        lines = [""] * (self.max_depth * 2 + 1)
        self.inorder(self.root, lines, False, -1)
        print()
        result = "Tree:```"
        for line in lines:
            result += "\n" + line
        return result + "\n```"











