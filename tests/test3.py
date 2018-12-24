
import sys
import test4 as t
import json
import os
print os.getcwd(),'\n'
print __file__,'\n'
print 'basename:', os.path.basename(__file__),'\n'
print 'dirname:',os.path.dirname(__file__),'\n'
print  os.path.abspath(__file__),'\n'
print os.path.dirname(os.path.abspath(__file__)),'\n'
print os.path.curdir,'\n'
print os.path.pardir,'\n'
print  os.path.abspath(os.path.curdir),'\n'
class A():
    with open('./test.json') as f:
        class_val = json.load(f)

    def __init__(self, **val):
        self.val = val

val_a = {'val4':1,'val5':2, 'val6':3}
val_b = {'val1':1,'val2':2, 'val3':3}

a1 = A(val1=1,val2=2,val3=3)
print a1.class_val
a1.class_val['shape'] = 'rectangle'
a2 = A()  
print a2.class_val