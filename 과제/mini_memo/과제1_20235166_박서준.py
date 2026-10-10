"""
2026-FALL-DataStructure
[자료구조 과제] 이중 연결 리스트로 미니 메모장 만들기

학번: 20235166
이름: 박서준
"""

AUTOSAVE_FILE = "autosave.txt"
AUTOSAVE_EVERY = 5


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        #맨 위에 item을 넣는다
        self.items.append(item)

    def pop(self):
        #맨 위 원소를 제거하여 반환한다
        try:
            return self.items.pop()
        except:
            raise IndexError

    def is_empty(self):
        #비어 있으면 True, 아니면 False를 반환한다
        return len(self.items) == 0

    def clear(self):
        self.items = []


class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def insert(self, index, data):
        """
        data를 삽입하여 새 줄이 index번째가 되게 한다. 1~size+1만 가능하며 그 밖이면 IndexError.
        index가 size+1이면 맨 끝에 붙는다. prev/next 연결과 head/tail/size를 갱신한다.
        빈 리스트 / 맨 앞 / 맨 끝 / 중간 삽입은 바꿔야 할 연결이 서로 다르다.
        아래 작성 완료된 node_at 메서드는 1~size만 받는다.
        """

        if index < 1 or index > self.size + 1:
            raise IndexError

        new_node = Node(data)

        # 빈 리스트
        if self.size == 0:
            self.head = new_node
            self.tail = new_node
        # 맨 앞
        elif index == 1:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        # 맨 끝
        elif index == self.size + 1:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        # 중간 삽입
        else:
            next_node = self.node_at(index)
            prev_node = next_node.prev
            new_node.prev = prev_node
            new_node.next = next_node
            prev_node.next = new_node
            next_node.prev = new_node

        self.size += 1

    def delete(self, index):
        """
        index번째 줄을 삭제하고 지운 문자열을 반환한다.
        1~size만 가능하며 그 밖이면 IndexError. prev/next 연결과 head/tail/size를 갱신한다.
        노드가 하나뿐일 때 / 맨 앞 / 맨 끝 / 중간 삭제는 바꿔야 할 연결이 서로 다르다.
        """

        if index < 1 or index > self.size:
            raise IndexError

        target_node = self.node_at(index)
        text = target_node.data

        # 노드가 하나뿐일 때 삭제
        if self.size == 1:
            self.head = None
            self.tail = None
        # 맨 앞 삭제
        elif target_node is self.head:
            self.head = target_node.next
            self.head.prev = None
        # 맨 끝 삭제
        elif target_node is self.tail:
            self.tail = target_node.prev
            self.tail.next = None
        # 중간 삭제
        else:
            target_node.prev.next = target_node.next
            target_node.next.prev = target_node.prev

        self.size -= 1
        return text

    # 아래 보면 탐색·출력용 메서드(node_at, to_text_list)는 완성되어 있음
    def node_at(self, index):
        if index < 1 or index > self.size:
            raise IndexError("없는 줄 번호")
        node = self.head
        for _ in range(index - 1):
            node = node.next
        return node

    def to_text_list(self):
        result = []
        node = self.head
        while node is not None:
            result.append(node.data)
            node = node.next
        return result


class Editor:
    """
    두 스택(undo_stack, redo_stack)으로 실행취소(undo)·재실행(redo) 구현하기

    [동작 예시]
      append A, append B  -> 메모: A, B       undo_stack: [A추가, B추가]
      undo                -> 메모: A          B추가를 취소하고 redo_stack으로 옮김
      redo                -> 메모: A, B       B추가를 다시 하고 undo_stack으로 옮김
      undo 후 새 편집     -> redo_stack을 비움 (되살릴 수 없게 됨)

    [무엇을 기록할까?]
      편집 하나를 되돌리려면 "무슨 작업을, 몇 번째 줄에, 어떤 내용으로" 했는지 알아야 합니다.
      세 값을 하나로 묶어 스택에 넣으면 됩니다. 묶는 방법은 자유이며, 예를 들면:
          self.undo_stack.push(("insert", 3, "hello"))     # 괄호로 묶은 것을 튜플이라 함
          action, index, text = self.undo_stack.pop()      # 꺼낼 때 세 변수로 나눠 받기
      리스트 ["insert", 3, "hello"]로 묶어도 됩니다.
      삽입을 되돌리려면 그 줄을 삭제하고, 삭제를 되돌리려면 지운 내용을 그 자리에 다시 삽입합니다.
    """
    def __init__(self):
        self.lines = DoublyLinkedList()
        self.cursor = None
        self.undo_stack = Stack()
        self.redo_stack = Stack()
        self.change_count = 0

    def insert(self, index, text):
        """
        _insert_line으로 삽입한 뒤 작업을 기록하고, redo_stack을 비우고, changed()를 호출한다.
        (삽입을 먼저 해야 없는 줄 번호일 때 IndexError가 나면서 아무것도 기록되지 않는다.)
        """
        self._insert_line(index, text)
        self.undo_stack.push(("insert", index, text))
        self.redo_stack.clear()
        self.changed()

    def delete(self, index):
        """
        _delete_line으로 삭제한 뒤 복원에 필요한 정보를 기록하고, redo_stack을 비우고, changed()를 호출한다.
        (_delete_line은 지운 내용을 반환한다.)
        """
        text = self._delete_line(index)
        self.undo_stack.push(("delete", index, text))
        self.redo_stack.clear()
        self.changed()

    def undo(self):
        """
        최근 편집을 취소한다. 작업이 없으면 False, 수행했으면 True.
        되돌릴 때는 _insert_line/_delete_line을 직접 사용한다(self.insert/self.delete를
        쓰면 기록이 다시 쌓이고 redo 기록이 지워진다). 취소한 작업은 redo 스택으로 옮기고 changed()를 호출한다.
        """
        if self.undo_stack.is_empty():
            return False

        action, index, text = self.undo_stack.pop()
        if action == "insert":
            self._delete_line(index)
        else:
            self._insert_line(index, text)

        self.redo_stack.push((action, index, text))
        self.changed()
        return True

    def redo(self):
        """
        취소했던 편집을 다시 수행한다. 작업이 없으면 False, 수행했으면 True.
        undo와 마찬가지로 _insert_line/_delete_line을 사용하고, 다시 수행한 작업은 undo 스택으로 옮기고 changed()를 호출한다.
        """
        if self.redo_stack.is_empty():
            return False

        action, index, text = self.redo_stack.pop()
        if action == "insert":
            self._insert_line(index, text)
        else:
            self._delete_line(index)

        self.undo_stack.push((action, index, text))
        self.changed()
        return True

    def up(self):
        """cursor.prev를 이용해 한 줄 위로 이동한다. 처음이나 빈 메모에서는 머문다."""
        if self.cursor is not None and self.cursor.prev is not None:
            self.cursor = self.cursor.prev

    def down(self):
        """cursor.next를 이용해 한 줄 아래로 이동한다. 끝이나 빈 메모에서는 머문다."""
        if self.cursor is not None and self.cursor.next is not None:
            self.cursor = self.cursor.next

    def autosave(self):
        """
        현재 메모 전체를 AUTOSAVE_FILE에 덮어써서 저장한다. 메모 한 줄을 파일 한 줄에 쓴다.
        한글이 깨지지 않도록 encoding="utf-8"로 연다.
        """
        with open(AUTOSAVE_FILE, "w", encoding="utf-8") as saved_file:
            node = self.lines.head
            while node is not None:
                saved_file.write(node.data + "\n")
                node = node.next

    # 이 메서드들은 스택에 직접 넣지 않습니다.
    # 이하 메서드들은 완성되어 있음
    def current_index(self): 
        """현재 노드에서 prev를 따라 현재 줄 번호를 구한다(1부터)."""
        if self.cursor is None:
            raise IndexError("현재 줄이 없습니다.")
        index = 1
        node = self.cursor
        while node.prev is not None:
            node = node.prev
            index += 1
        return index

    def insert_current(self, text): 
        """현재 줄 앞에 삽입한다. 빈 메모에서는 첫 줄을 만든다."""
        index = 1 if self.cursor is None else self.current_index()
        self.insert(index, text)

    def delete_current(self):
        """현재 줄을 삭제한다. 빈 메모에서는 IndexError."""
        self.delete(self.current_index())

    def _insert_line(self, index, text):
        self.lines.insert(index, text)
        if self.cursor is None:
            self.cursor = self.lines.head

    def _delete_line(self, index):
        target = self.lines.node_at(index)
        successor, predecessor = target.next, target.prev
        text = self.lines.delete(index)
        if self.cursor is target:
            self.cursor = successor if successor is not None else predecessor
        return text

    def append(self, text):
        self.insert(self.lines.size + 1, text)

    def changed(self):
        """편집 횟수를 세고, AUTOSAVE_EVERY번마다 자동저장한다. 커서 이동(up/down)에서는 부르지 않는다."""
        self.change_count += 1
        if self.change_count % AUTOSAVE_EVERY == 0:
            self.autosave()
            print("  (자동저장 완료)")

    def show(self):
        if self.lines.head is None:
            print("  (빈 메모)")
            return
        node, index = self.lines.head, 1
        while node is not None:
            marker = ">" if node is self.cursor else " "
            print(f"  {marker} {index} | {node.data}")
            node, index = node.next, index + 1


def main():
    editor = Editor()
    print("미니 메모장 - 명령어: append, insert, delete, up, down, print, undo, redo, exit")
    print("insert 내용: 현재 줄 앞에 삽입 / delete: 현재 줄 삭제")
    print("up/down으로 편집할 줄을 선택하세요. print의 > 표시는 현재 줄입니다.")
    while True:
        try:
            command = input("> ").strip()
        except EOFError:
            break
        cmd, _, text = command.partition(" ")
        text = text.strip()
        try:
            if cmd == "append":
                editor.append(text)
            elif cmd == "insert":
                if not text:
                    print("  사용법: insert 내용")
                else:
                    editor.insert_current(text)
            elif cmd == "delete":
                if text:
                    print("  사용법: delete")
                else:
                    editor.delete_current()
            elif cmd == "up":
                editor.up()
            elif cmd == "down":
                editor.down()
            elif cmd == "print":
                editor.show()
            elif cmd == "undo":
                if not editor.undo():
                    print("  되돌릴 작업이 없습니다.")
            elif cmd == "redo":
                if not editor.redo():
                    print("  다시 할 작업이 없습니다.")
            elif cmd == "exit":
                break
            elif cmd:
                print("  알 수 없는 명령어입니다.")
        except IndexError:
            print("  현재 줄이 없습니다.")
    editor.autosave()
    print("자동저장 후 종료합니다.")


if __name__ == "__main__":
    main()
