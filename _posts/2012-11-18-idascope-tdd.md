---
layout:             post
title:              "TDD & IDAPython"
author:             Daniel Plohmann
date:               2012-11-18 01:00:00 +0100
last_modified_at:   2012-11-18 01:00:00 +0100
categories:         blog
tags:               idascope
---

This is just a short note in which I want to share my experiences with writing test code for (IDAPython) scripts I use and produce on a daily basis.  

### The case for Test-Driven Development

A while ago, I thought it would be a good idea to advance my coding skills. 
So I had a look around methodologies that are popular in software development but that I had not tried myself.   
The best candidate seemed to me Test-Driven Development (TDD) as I was familiar with the concept of unit testing but I was not able to believe that TDD can drive architecture and design decisions.   
  
I started reading the [Clean Code][amazon clean code] series of books by Uncle Bob. 
The books start out with general advice on how to structure your code in a way it is easier to understand and maintain. 
I recognize these books as an efficient way to lift your own coding habits to an acceptable level if you plan on publishing code.  
In the later chapters the book focusses on TDD. 
I transferred the given example projects to Python (instead of Java, which the book uses) and really tried hard to embrace TDD as driving method for code generation.  
  
- Well, didn't work out so far for me. ;)  
Personally, I still have the impression TDD slows me down too hard when initially implementing functionality. 
That's because there is only a very limited time frame when doing analyses and helper scripts are mostly tailored to specific use cases and often not part of the analysis result. 
So the code has limited value to me.  
Additionally, refactoring and restructuring can probably become more painful as you obviously have to change both production and testing code. 
But this is a wrong assumption as I will later point out.  
However, I understand the argument that finding & fixing bugs is more expensive in regards of time than preventing to having bugs in first place. 
But as my projects (helper scripts) usually have a few hundred lines at most and many are even one-shot tools, the overhead does not fit. 
For large projects, I would definitely give TDD a shot.  
  
Nevertheless, over trying TDD, I really started liking to have tests for my code for the following reasons:  
 * Tests give me increasing confidence instead of the feeling that I'm piling up a house of cards that may collapse with additions.
 * Writing tests to fix bugs both documents the bugs and offers valuable insights in my shortcomings when writing the code in first place. Helps to avoid the same errors in the future.
 * My code itself has become much more modular as I'm looking out to have it testable. Refactorings actually have become easier.
 * Tests come in as a free documentation on how to actually use the code, both a help for myself (looking my code again after some months) as well as for others.
 * I only have to write tests for parts of the code I think that are worth being covered by tests ("complex"), indicated by me having had to think about them for some time before simply pinning them down.
 * Executing successful tests is quite satisfying.

So I regularly produce "test-covered" code now, instead of "test-driven" code which I'm pretty happy with. 
Should have done that with IDAscope as well but I'll add tests for all future bugs I find, I guess.  

### Tests in IDAPython

So how to use this now in IDA?
Here is my template file for writing tests:
```
import sys
import unittest
import datetime
from test import *

import idautils

class IDAPythonTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_fileLoaded(self):
        assert idautils.GetInputFileMD5() is not None


def main(argv):
    print "#" * 10 + " NEW TEST RUN ## " \
        + datetime.datetime.utcnow().strftime("%A, %d. %B %Y %I:%M:%S") \
        + " " + "##"
    unittest.main()


if __name__ == "__main__":
    sys.exit(main(sys.argv))

```  
In this template we have only one test in our test case `IDAPythonTests` called `test_fileLoaded`. 
Tests to be executed by the Python [unittes][python unittest] testrunner use the prefix `test_`.  
Normally you would not test directly against IDAPython's API as in this example.
But would rather test your own code through function calls, with your code usually being located in a different file and imported into the test case.  
  
You can run this as a script within IDA while having loaded a file for analysis. 
This allows you to specifically test your code against IDAPython's API on the one hand and using the contents of the file under analysis for verification on the other hand.  
The output of the above script while having loaded a file and not having loaded a file to demonstrate the test's behaviour looks like this:  
```
---------------------------------------------------------------------------------
Python 2.7.2 (default, Jun 12 2011, 15:08:59) [MSC v.1500 32 bit (Intel)] 
IDAPython v1.5.5 final (c) The IDAPython Team <idapython@googlegroups.com>
---------------------------------------------------------------------------------
########## NEW TEST RUN ## Sunday, 18. November 2012 11:49:29 ##
.
----------------------------------------------------------------------
Ran 1 test in 0.010s

OK
########## NEW TEST RUN ## Sunday, 18. November 2012 11:50:06 ##
F
======================================================================
FAIL: test_fileLoaded (__main__.IDAPython_Tests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "Z:/ida_tests.py", line 14, in test_fileLoaded
    assert idautils.GetInputFileMD5() is not None
AssertionError

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```
Pretty much the IDAPython shell we are used to + the nice output from Python's unit testing framework.

*[link to original post on blogspot][blogspot post].*

[amazon clean code]: http://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882
[python unittest]: http://docs.python.org/2/library/unittest.html
[blogspot post]: https://pnx-tf.blogspot.com/2012/11/tdd-idapython.html