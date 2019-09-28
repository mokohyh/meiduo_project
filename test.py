class A():
    def __init__(self, xx = None):
        if not xx:
            self.xx = xx
        self.xx = "11111"

    def pas(self):
        print(self.xx)


gg = A("000")
gg.pas()
