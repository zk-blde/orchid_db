import threading
from random import randint, randrange

from mapEngine.base import BaseMapWrapper


class Node:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.children = []


class BTree:

    def __init__(self, t):
        """
        Initializing the B-Tree
        :param t: Order.
        """
        self.root = Node(True)
        self.t = t

    def printTree(self, x, lvl=0):
        """
        Prints the complete B-Tree
        :param x: Root node.
        :param lvl: Current level.
        """
        print("Level ", lvl, " --> ", len(x.keys), end=": ")
        for i in x.keys:
            print(i, end=" ")
        print()
        lvl += 1
        if len(x.children) > 0:
            for i in x.children:
                self.printTree(i, lvl)

    def search(self, k, x=None):
        """
        Search for key 'k' at position 'x'
        :param k: The key to search for.
        :param x: The position to search from. If not specified, then search occurs from the root.
        :return: 'None' if 'k' is not found. Otherwise returns a tuple of (node, index) at which the key was found.
        """
        if x is not None:
            i = 0
            while i < len(x.keys) and k > x.keys[i][0]:
                i += 1
            if i < len(x.keys) and k == x.keys[i][0]:
                return x, i
            elif x.leaf:
                return None
            else:
                # Search its children
                return self.search(k, x.children[i])
        else:
            # Search the entire tree
            return self.search(k, self.root)

    def insert(self, k):
        """
        Calls the respective helper functions for insertion into B-Tree
        :param k: The key to be inserted.
        """
        root = self.root
        # If a node is full, split the child
        if len(root.keys) == (2 * self.t) - 1:
            temp = Node()
            self.root = temp
            # Former root becomes 0'th child of new root 'temp'
            temp.children.insert(0, root)
            self._splitChild(temp, 0)
            self._insertNonFull(temp, k)
        else:
            self._insertNonFull(root, k)

    def _insertNonFull(self, x, k):
        """
        Inserts a key in a non-full node
        :param x: The key to be inserted.
        :param k: The position of node.
        """
        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append((None, None))
            while i >= 0 and k[0] < x.keys[i][0]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
        else:
            while i >= 0 and k[0] < x.keys[i][0]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == (2 * self.t) - 1:
                self._splitChild(x, i)
                if k[0] > x.keys[i][0]:
                    i += 1
            self._insertNonFull(x.children[i], k)

    def _splitChild(self, x, i):
        """
        Splits the child of node at 'x' from index 'i'
        :param x: Parent node of the node to be split.
        :param i: Index value of the child.
        """
        t = self.t
        y = x.children[i]
        z = Node(y.leaf)
        x.children.insert(i + 1, z)
        x.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t: (2 * t) - 1]
        y.keys = y.keys[0: t - 1]
        if not y.leaf:
            z.children = y.children[t: 2 * t]
            y.children = y.children[0: t - 1]

    def delete(self, x, k):
        """
        Calls the respective helper functions for deletion from B-Tree
        :param x: The node, according to whose relative position, helper functions are called.
        :param k: The key to be deleted.
        """
        t = self.t
        i = 0
        while i < len(x.keys) and k[0] > x.keys[i][0]:
            i += 1
        # Deleting the key if the node is a leaf
        if x.leaf:
            if i < len(x.keys) and x.keys[i][0] == k[0]:
                x.keys.pop(i)
                return
            return

        # Calling '_deleteInternalNode' when x is an internal node and contains the key 'k'
        if i < len(x.keys) and x.keys[i][0] == k[0]:
            return self._deleteInternalNode(x, k, i)
        # Recursively calling 'delete' on x's children
        elif len(x.children[i].keys) >= t:
            self.delete(x.children[i], k)
        # Ensuring that a child always has atleast 't' keys
        else:
            if i != 0 and i + 2 < len(x.children):
                if len(x.children[i - 1].keys) >= t:
                    self._deleteSibling(x, i, i - 1)
                elif len(x.children[i + 1].keys) >= t:
                    self._deleteSibling(x, i, i + 1)
                else:
                    self._deleteMerge(x, i, i + 1)
            elif i == 0:
                if len(x.children[i + 1].keys) >= t:
                    self._deleteSibling(x, i, i + 1)
                else:
                    self._deleteMerge(x, i, i + 1)
            elif i + 1 == len(x.children):
                if len(x.children[i - 1].keys) >= t:
                    self._deleteSibling(x, i, i - 1)
                else:
                    self._deleteMerge(x, i, i - 1)
            self.delete(x.children[i], k)

    def _deleteInternalNode(self, x, k, i):
        """
        Deletes internal node
        :param x: The internal node in which key 'k' is present.
        :param k: The key to be deleted.
        :param i: The index position of key in the list
        """
        t = self.t
        # Deleting the key if the node is a leaf
        if x.leaf:
            if x.keys[i][0] == k[0]:
                x.keys.pop(i)
                return
            return

        # Replacing the key with its predecessor and deleting predecessor
        if len(x.children[i].keys) >= t:
            x.keys[i] = self._deletePredecessor(x.children[i])
            return
        # Replacing the key with its successor and deleting successor
        elif len(x.children[i + 1].keys) >= t:
            x.keys[i] = self._deleteSuccessor(x.children[i + 1])
            return
        # Merging the child, its left sibling and the key 'k'
        else:
            self._deleteMerge(x, i, i + 1)
            self._deleteInternalNode(x.children[i], k, self.t - 1)

    def _deletePredecessor(self, x):
        """
        Deletes predecessor of key 'k' which is to be deleted
        :param x: Node
        :return: Predecessor of key 'k' which is to be deleted
        """
        if x.leaf:
            return x.keys.pop()
        n = len(x.keys) - 1
        if len(x.children[n].keys) >= self.t:
            self._deleteSibling(x, n + 1, n)
        else:
            self._deleteMerge(x, n, n + 1)
        self._deletePredecessor(x.children[n])

    def _deleteSuccessor(self, x):
        """
        Deletes successor of key 'k' which is to be deleted
        :param x: Node
        :return: Successor of key 'k' which is to be deleted
        """
        if x.leaf:
            return x.keys.pop(0)
        if len(x.children[1].keys) >= self.t:
            self._deleteSibling(x, 0, 1)
        else:
            self._deleteMerge(x, 0, 1)
        self._deleteSuccessor(x.children[0])

    def _deleteMerge(self, x, i, j):
        """
        Merges the children of x and one of its own keys
        :param x: Parent node
        :param i: The index of one of the children
        :param j: The index of one of the children
        """
        cNode = x.children[i]

        # Merging the x.children[i], x.children[j] and x.keys[i]
        if j > i:
            rsNode = x.children[j]
            cNode.keys.append(x.keys[i])
            # Assigning keys of right sibling node to child node
            for k in range(len(rsNode.keys)):
                cNode.keys.append(rsNode.keys[k])
                if len(rsNode.children) > 0:
                    cNode.children.append(rsNode.children[k])
            if len(rsNode.children) > 0:
                cNode.children.append(rsNode.children.pop())
            new = cNode
            x.keys.pop(i)
            x.children.pop(j)
        # Merging the x.children[i], x.children[j] and x.keys[i]
        else:
            lsNode = x.children[j]
            lsNode.keys.append(x.keys[j])
            # Assigning keys of left sibling node to child node
            for i in range(len(cNode.keys)):
                lsNode.keys.append(cNode.keys[i])
                if len(lsNode.children) > 0:
                    lsNode.children.append(cNode.children[i])
            if len(lsNode.children) > 0:
                lsNode.children.append(cNode.children.pop())
            new = lsNode
            x.keys.pop(j)
            x.children.pop(i)

        # If x is root and is empty, then re-assign root
        if x == self.root and len(x.keys) == 0:
            self.root = new

    @staticmethod
    def _deleteSibling(x, i, j):
        """
        Borrows a key from j'th child of x and appends it to i'th child of x
        :param x: Parent node
        :param i: The index of one of the children
        :param j: The index of one of the children
        """
        cNode = x.children[i]
        if i < j:
            # Borrowing key from right sibling of the child
            rsNode = x.children[j]
            cNode.keys.append(x.keys[i])
            x.keys[i] = rsNode.keys[0]
            if len(rsNode.children) > 0:
                cNode.children.append(rsNode.children[0])
                rsNode.children.pop(0)
            rsNode.keys.pop(0)
        else:
            # Borrowing key from left sibling of the child
            lsNode = x.children[j]
            cNode.keys.insert(0, x.keys[i - 1])
            x.keys[i - 1] = lsNode.keys.pop()
            if len(lsNode.children) > 0:
                cNode.children.insert(0, lsNode.children.pop())


# The demo function
def demo():
    B = BTree(3)
    B.insert((1, "value"))
    B.insert((2, "value1"))
    B.insert((3, "value2"))
    B.insert((4, "value3"))
    B.insert((6, "value3"))
    B.insert((6, "value4"))

    index = B.search(6)[1]
    keys = B.search(6)[0].keys
    print(keys[index])

    # Insert
    customNo = 10
    for i in range(customNo):
        B.insert((str(i), str(randint(i, 5 * i))))
    B.printTree(B.root)
    print()

    # Delete
    toDelete = randint(0, customNo)
    print("Key {} deleted!".format(toDelete))
    B.delete(B.root, (toDelete,))
    # B.delete(B.root, (4,))
    B.printTree(B.root)
    print()

    # Search
    toSearch = randrange(0, 2 * customNo)
    if B.search(toSearch) is not None:
        print("Key {} found!".format(toSearch))
    else:
        print("Key {} not found!".format(toSearch))


class BTreeWrapper(BaseMapWrapper):
###########################################################################
#??????????????????????????????????????????????????????
    _instance_lock = threading.Lock()
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with BTreeWrapper._instance_lock:
                if not hasattr(cls, '_instance'):
                    BTreeWrapper._instance = super().__new__(cls)

            return BTreeWrapper._instance
############################################################################
    def __init__(self):
        self.btree_core = BTree(3)

    def __setitem__(self, key, value):
        assert type(key) == str
        node = self.btree_core.search(key)
        if node is not None:
            self.btree_core.delete(self.btree_core.root, (key,))
        self.btree_core.insert((key, value))

    def __getitem__(self, key):
        assert type(key) == str
        value = self.get(key)
        if not value:
            raise KeyError
        else:
            return value

    def get(self, key):
        assert type(key) == str
        node = self.btree_core.search(key)
        if node is not None:
            index = node[1]
            keys = node[0].keys
            return keys[index]
        else:
            return None

    def _del(self, key):
        assert type(key) == str
        self.btree_core.delete(self.btree_core.root, (key,))

    def __delitem__(self, key):
        assert type(key) == str
        return self._del(key)

    def pop(self, key):
        assert type(key) == str
        return self._del(key)


# Program starts here
if __name__ == '__main__':
    p = BTreeWrapper()
    p["123"] = "666"
    p["234"] = "666"
    p["456"] = "666"
    print(p["123"])
    print(p["234"])
    print(p["456"])
    p["123"] = "777"
    print(p["123"])
    p.pop("123")
    print(p.get("123"))

    j = BTreeWrapper()
    print(p["234"])
    print(p["456"])
