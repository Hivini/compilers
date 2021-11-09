import unittest

from compiler.parser import ASTTypes, Parser


class TestParser(unittest.TestCase):

    def setUp(self):
        self.instance = Parser()
        self.parser = self.instance.createParser()

    def testPrintExp(self):
        tree = self.parser.parse('print(a);')
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].type, ASTTypes.PRINT)
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].type, ASTTypes.VARIABLE)
        self.assertEqual(tree.children[0].children[0].value, 'a')
        self.assertEqual(self.instance.total_errors, 0)

    def testPrintExpInvalid(self):
        tree = self.parser.parse('print(a)')
        self.assertEqual(tree, None)
        self.assertEqual(self.instance.total_errors, 1)
