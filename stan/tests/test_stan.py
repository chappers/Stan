# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 12:54:30 2014

@author: Chapman
"""

import unittest
from stan import stan

class Test_stan(unittest.TestCase):  
    #"test=test\ntest=describe.describe(data=test,by='sex',var='age')\ntest1=test\n"
    def test_parse(self):
        cstr = """
    Data test;
        set test;
      run;
      
    proc describe data = test out = test;
        by sex;
        var age;
    run;
    
    data test1;
        set test;
    run;
    
    """
        self.assertTrue(stan.transcompile(cstr) == "test=test\ntest=describe.describe(data=test,by='sex',var='age')\ntest1=test\n")
    
if __name__ == '__main__':
    unittest.main()