from typing import List
from compiler.parser import ASTNode, ASTTypes
from compiler.semantics import SemanticAnalyzer


class TACProcessor:

    def __init__(self, astroot: ASTNode) -> None:
        self.astroot = astroot
        self.tmpGen = self._tempGenerator()

    def _tempGenerator(self) -> str:
        """Generates temporal variable names."""
        counter = 0
        while True:
            yield f"t{counter}"
            counter += 1

    def _getNodeValue(self, node: ASTNode):
        if node.type == ASTTypes.VARIABLE:
            return node.variableName
        else:
            return node.variableValue

    def _generateAlgebraTAC(self, node: ASTNode, currentLines: List[str]):
        leftNode = node.children[0]
        rightNode = node.children[1]
        leftVar = self._getNodeValue(leftNode)
        rightVar = self._getNodeValue(rightNode)
        if leftNode.type in SemanticAnalyzer.algebraOp:
            leftVar = self._generateAlgebraTAC(leftNode, currentLines)
        if rightNode.type in SemanticAnalyzer.algebraOp:
            rightVar = self._generateAlgebraTAC(rightNode, currentLines)
        tmpVar = next(self.tmpGen)
        currentLines.append(f'{tmpVar} = {leftVar} + {rightVar}')
        return tmpVar

    def _generateTACHelper(self, node: ASTNode, currentLines: List[str]):
        if node.type in SemanticAnalyzer.declarationTypes:
            # Assign > First operation
            firstop = node.children[0].children[0]
            if firstop.type in SemanticAnalyzer.algebraOp:
                tmpVar = self._generateAlgebraTAC(firstop, currentLines)
            else:
                tmpVar = self._getNodeValue(node)
            currentLines.append(f'int {node.variableName} = {tmpVar}')
        else:
            for c in node.children:
                self._generateTACHelper(c, currentLines)

    def generateTAC(self):
        lines = []
        self._generateTACHelper(self.astroot, lines)
        return lines

    def generateTACPrint(self):
        lines = []
        self._generateTACHelper(self.astroot, lines)
        i = 1
        for line in lines:
            print(f'{i})\t{line}')
            i += 1
