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

from messaging.message import Message, COMPRESSORS
import messaging.message as message
from messaging.generator import Generator
from messaging.error import MessageError
import os
import re
import sys
import unittest

try:
    range=xrange
except NameError:
    pass

MESSAGE_CONVERT_OPTIONS = [dict(),]
for compressor in COMPRESSORS:
    MESSAGE_CONVERT_OPTIONS.append({'compression' : compressor})

_COMPLIANCE_NAME = "^[a-z0-9]{32}([\.-]{1}\d+)*$"
COMPLIANCE_NAME = re.compile(_COMPLIANCE_NAME)
EMPTY_BYTES = ''.encode()

def empty_string():
    """ Return empty unicode string based on python version. """
    try:
        return unicode('')
    except NameError:
        return ''

class MessageTest(unittest.TestCase):

    def setUp(self):
        """ Setup the test environment. """
    
    def tearDown(self):
        """ Restore the test environment. """
    
    def iterate(self, func):
        """ Iterate over body_content type and size
        and call giveb function.
        """
        types = ['index', 'text', 'binary', 'base64']
        header_count = -5
        for type in types:
            for size in [0, 1024, 10240, 102400]:
                func(body_content=type,
                     body_size=size,
                     header_count=header_count)
                
    def test_message_creation(self):
        """ Test message creation. """
        print("checking message creation")
        msg = Message(body='dfhkdfgkfd' , header={'l':'ff'})
        print("...message creation ok")
        
    def test_message_compression(self):
        """ Test message compression. """
        print("checking message compression")
        length = 10000
        body = ''.join(['a' for each in range(length)])
        ok = list()
        for module in COMPRESSORS:
            msg = Message(body=body , header={'l':'ff'})
            jsonified = msg.jsonify({'compression' : module})
            self.assert_(len(jsonified['body']) < length * 0.9,
                         "message should have been compressed with %s" %
                         module)
            ok.append(module)
        print("...message compression ok for %s" % ",".join(ok))
    
    def test_message_fullchain(self):
        """
        Test message fullchain.
        Generate a message, serialize it and deserialize it, the result should
        be equal to the first generated message.
        """
        print("checking message fullchain")
        self.iterate(self.__fullchain)
        print("...message fullchain ok")
    
    def __fullchain(self, **kwargs):
        gen = Generator(**kwargs)
        msgA = gen.message()
        msgB = message.deserialize(msgA.serialize())
        self.assertEqual(msgA.size(), msgB.size(), 
                         "message size not matching")
        self.assertEqual(msgA, msgB,
                         "Error, not the same after serialization")
        msgC = msgA.clone()
        self.assertEqual(msgA, msgC,
                         "Error, not the same after cloning\n%s\n%s\n" %
                         (msgA, msgC))
                
    def test_message_jsonify(self):
        """
        Test message jsonification.
        Generate a message, jsonify it and dejsonify it, the result should
        be equal to the first generated message.
        """
        print("checking message jsonification")
        self.iterate(self.__jsonify)
        print("...message jsonification ok")
    
    def __jsonify(self, **kwargs):
        gen = Generator(**kwargs)
        msg = gen.message()
        for option in MESSAGE_CONVERT_OPTIONS:
            jsonified = msg.jsonify(option)
            msgB = message.dejsonify(jsonified)
        self.assertEqual(msg, msgB, "Error in de/jsonification:\n%s\n%s\n" %
                         (msg, msgB))
    
    def test_message_stringify(self):
        """
        Test message stringification.
        Generate a message, stringify it and destringify it, the result should
        be equal to the first generated message.
        """
        print("checking message stringification")
        self.iterate(self.__stringify)
        print("...message stringification ok")
    
    def __stringify(self, **kwargs):
        gen = Generator(**kwargs)
        msg = gen.message()
        for option in MESSAGE_CONVERT_OPTIONS:
            stringified = msg.stringify(option)
            msgB = message.destringify(stringified)
            self.assertEqual(msg, msgB,
                             "Error in de/stringification:\n%s\n%s\n" %
                             (msg, msgB))
    
    def test_message_serialize(self):
        """
        Test message serialization.
        Generate a message, serialize it and deserialize it, the result should
        be equal to the first generated message.
        """
        print("checking message serialization")
        self.iterate(self.__serialize)
        print("...message serialization ok")
        
    def __serialize(self, **kwargs):
        gen = Generator(**kwargs)
        msg = gen.message()
        for option in MESSAGE_CONVERT_OPTIONS:
            serialized = msg.serialize(option)
            msgB = message.deserialize(serialized)
            self.assertEqual(msg, msgB, "Error in de/serialization")
            
    def test_md5(self):
        """
        Test message checksum.
        Generate a message, calculate its checksum and make some checks.
        """
        print("checking message checksum")
        self.iterate(self.__md5)
        print("... message checksum ok")
    
    def __md5(self, **kwargs):
        gen = Generator(**kwargs)
        checksum = gen.message().md5()
        self.assert_(len(checksum) == 32, "checksum length is not 32")
                
    def test_messages_compliance(self):
        """
        Test message compliance.
        Deserialize messages in test/compliance, and check that their checksum
        correspond to their filename.
        This allow to prove interoperability between Perl and Python
        implementations.
        """
        print("checking message compliance")
        path = ["test/compliance", ]
        counter = 0
        for folder in path:
            content = sorted(os.listdir(folder))
            for each in content:
                if not COMPLIANCE_NAME.match(each):
                    continue
                filer = open("%s/%s" % (folder, each), 'rb')
                serialized = EMPTY_BYTES.join(filer.readlines())
                filer.close()
                try:
                    msg = message.deserialize(serialized)
                except MessageError:
                    error = sys.exc_info()[1]
                    if "decoding supported but not installed" in \
                        "%s" % error:
                        print("skipping compliance test for %s: %s" % (each,
                                                                   error))
                    else:
                        raise error
                md5 = re.split('[\.-]', each)[0]
                msg_md5 = msg.md5()
                self.assertEqual(md5, msg_md5,
                                 "deserialization of %s failed:%s\nresult:%s"
                                % (each, msg, msg_md5))
                counter += 1
        print("...compliance ok, checked for %s messages" % counter)
        
if __name__ == "__main__":
    unittest.main()  
