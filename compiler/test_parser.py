import unittest

from compiler.parser import Parser


class TestParser(unittest.TestCase):

    def setUp(self):
        self.instance = Parser()
        self.parser = self.instance.createParser()

    def testPrintExp(self):
        self.parser.parse('print(a);')
        self.assertEqual(self.instance.total_errors, 0)

    def testPrintExpInvalid(self):
        self.parser.parse('print(a)')
        self.assertEqual(self.instance.total_errors, 1)
