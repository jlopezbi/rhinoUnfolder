
class Base(object):
    def __init__(self,A,B):
        self.A = A
        self.B = B 

    def baseBehavior(self):
        print "A",
        print self.A
        print "B",
        print self.B

class Derived(Base):
    def __init__(self,A,B,C):
        Base.__init__(self,A,B)
        self.C = C

    def derivedBehavior(self):
        print "C"
        print self.C

class Base2(object):
    def __init__(self,kwargs):
        self.A = kwargs.get('A',0)
        self.B = kwargs['B']

    def base2Behavior(self):
        print "A and B:",
        print self.A
        print self.B

class Derived2(Base2):
    def __init__(self,**kwargs):
        Base2.__init__(self,kwargs)
        self.C = kwargs.get('C','c')

    def derived_2_behavior(self):
        print "C:",
        print self.C
