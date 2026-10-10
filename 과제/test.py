class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        self.items.pop()

    def is_empty(self):
        if len(self.items) == 0:
            print("True")
        else:
            print("False")
    def clear(self):
        self.items = []

    def print_stack(self):
        print(self.items)

stack1 = Stack()
stack1.push(1)
stack1.print_stack()
stack1.is_empty()

stack1.push(1)
stack1.push(2)
stack1.print_stack()
stack1.clear()
stack1.print_stack()
