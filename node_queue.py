class Node:

    def __init__(self, newurl, title, trueurl):
        self.next = None
        self.prev = None
        self.url = newurl
        self.title = title
        self.true_url = trueurl

    def __repr__(self):
        if self.url is None:
            print("None Node")
        else:
            print(self.url)

    def get_newurl(self):
        return self.url

    def get_title(self):
        return self.title

    def get_true_url(self):
        return self.true_url

    def set_next(self, node):
        self.next = node

    def set_prev(self, node):
        self.prev = node


class node_queue:

    def __init__(self):

        self.tail = None
        self.head = None
        self.size = 0

    def __repr__(self):
        return str(self)

    def __str__(self):
        x = ""
        y = self.tail
        while y is not None:
            x = x + " " + y.get_newurl()
            y = y.next
        return x

    def get_tail(self):
        return self.tail

    def get_size(self):
        return self.size

    def pop(self):
        if self.size == 0:
            print("you just tried to pop an empty queue")
            return None
        x = self.head
        if x.prev is not None:
            x.prev.next = None
        self.head = x.prev
        self.size = self.size - 1
        return x

    def head_peep(self):
        return self.head

    def add(self, newurl, title=None, trueurl=None):
        x = Node(newurl, title, trueurl)
        x.next = self.tail
        if self.size == 0:
            self.head = x
        else:
            x.next.prev = x
        self.tail = x
        self.size = self.size + 1

    def remove(self, newurl):
        if self.head.get_url() == newurl and self.tail.get_url() == newurl:
            self.empty()
        elif self.tail.get_url() == newurl:
            self.tail.next.prev = None
            self.tail = self.tail.next
        elif self.head.get_url() == newurl:
            self.head.prev.next = None
            self.head = self.head.prev
        else:
            x = self.tail
            while x.url != newurl:
                x = x.next
            x.prev.next = x.next
            x.next.prev = x.prev
        self.size = self.size - 1

    def contains(self, newurl):
        if self.size == 0:
            return False
        x = self.tail
        while x.next is not None:
            if x.url == newurl:
                return True
            x = x.next
        return False


    def empty(self):
        self.head = None
        self.tail = None
        self.size = 0





