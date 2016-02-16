
class Base(object):
    def __init__(self,**kwargs):
        self.A = kwargs['A']
        self.B = kwargs['B']

    def baseBehavior(self):
        print "A: ",
        print self.A
        print "B :",
        print self.B

class DerivedC(Base):
    def __init__(self,**kwargs):
        Base.__init__(self,**kwargs)
        self.C = kwargs['C']

    def newBehavior(self):
        print "C",
        print self.C

class DerivedD(Base):
    def __init__(self,**kwargs):
        Base.__init__(self,**kwargs)
        self.D = kwargs['D']

    def newBehavior(self):
        print "D",
        print self.D
