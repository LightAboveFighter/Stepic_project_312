import pytest

def add(x, y):
    return x+y

def sub(x, y):
    return x-y

class A:
    def __init__(self, x: int, name: str):
        self.x = x
        self.name = name

class Segment:
    def __init__(self, x1: int, x2: int):
        self.start = x1
        self.finish = x2

    def move(self, dx: int):
        self.start += dx
        self.finish += dx

    def __repr__(self):
        return f"({self.start=}, {self.finish=})"
    
    def __str__(self):
        return f"({self.start}, {self.finish})"

    def __eq__(self, other):
        return self.start == other.start \
                and \
                self.finish == other.finish
    
# a = Segment(2, 10)
# print(a)
# print([a, a])
# print(repr(a))

def test_Segment_create():
    f = Segment(12, 18)
    assert f.start == 12
    assert f.finish == 18

def test_Segment_move():
    a = Segment(1, 3)
    a.move(5)
    assert a == Segment(6, 8)
    assert str(a) == "(6, 8)"
    
def test_A():
    b = A(12, "tanya")
    assert 12 == b.x
    assert "tanya" == b.name

def test_add():
    for i in range(-50, 50):
        for j in range(-50, 50):
            assert i + j == add(i, j)

@pytest.mark.parametrize("res, x, y", [
                         [5, 2, 3],
                         [7, 2, 5],
                         [-1, 9, -10]
])
def test_add2(res, x, y):
    assert res == add(x, y)

def test_sub():
    for i in range(-50, 50):
        for j in range(-50, 50):
            assert i - j == sub(i, j)


def send_status(*r):
    """ r - (requests.post object, strict requirment, ...)
    If strict requirment = 0 - every succes code will be enough """
    for i in range(1, len(r)+1, 2):
        if r[i] == 0:
            if not(r[i-1]):
                return "Failed"
            return "Succes"
        if r[i-1] != r[i]:
            return "Failed"
    return "Succes"