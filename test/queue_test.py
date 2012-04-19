# -*- coding: utf-8 -*-
"""
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
__version__ = "$Revision: 1 $"
# $Source$

from messaging.generator import Generator
import messaging.queue as queue
import os
import re
import shutil
import unittest

class QueueTest(unittest.TestCase):

    def setUp(self):
        """ Setup the test environment. """
        self.path = os.getcwd() + "/directory"
        shutil.rmtree(self.path, ignore_errors=True)
        self.generator = Generator(body_content="text",
                                   body_size=1024,
                                   header_count=5)
        
    def tearDown(self):
        """ Restore the test environment. """
        shutil.rmtree(self.path, ignore_errors=True)
        
    def __test_dq(self, qtype):
        """ Dirq base test. """
        print("checking %s queue" % qtype)
        option = {"type" : qtype,
                  "path" : "%s/%s" % (self.path, qtype), }
        try:
            dirq = queue.new(option)
        except SyntaxError:
            print(">>>>>>>> Dirq %s not supported in this Python version" %
                  qtype)
            return False
        except ImportError:
            print(">>>>>>>> Dirq %s not installed or not in PYTHONPATH" %
                  qtype)
            return False
        msg = self.generator.message()
        element = dirq.add_message(msg)
        msg2 = None
        if dirq.lock(element):
            msg2 = dirq.get_message(element)
            dirq.unlock(element)
        self.assertEqual(msg, msg2,
                         "messages should be equal:\n%s\n###\n%s" %
                         (msg, msg2))
        try:
            msg3 = dirq.dequeue_message(element)
            self.assertEqual(msg, msg3,
                             "messages should be equal:\n%s\n###\n%s" %
                             (msg, msg3))
        except AttributeError:
            print("dequeue method not supported by this queue type")
        print("...%s queue ok" % qtype)

    def test_queue_normal(self):
        """ Test normal dirq. """
        self.__test_dq("DQ")
            
    def test_queue_simple(self):
        """ Test simple dirq. """
        self.__test_dq("DQS")
        
    def test_queue_null(self):
        """ Test null dirq. """
        qtype = "NULL"
        print("checking %s queue" % qtype)
        option = {'type' : qtype}
        try:
            dirq = queue.new(option)
        except SyntaxError:
            print(">>>>>>>> Dirq %s not supported in this Python version" %
                  qtype)
            return False
        except ImportError:
            print(">>>>>>>> Dirq %s not installed or not in PYTHONPATH" %
                  qtype)
            return False
        msg = self.generator.message()
        element = dirq.add_message(msg)
        self.assertEqual(element, "", "add_message should return empty string")
        try:
            msg2 = dirq.get_message(element)
            raise AssertionError("null queue get_message should "
                                 "raise NotImplementedError")
        except NotImplementedError:
            pass
        print("...%s queue ok" % qtype)
            

if __name__ == "__main__":
    unittest.main()  
