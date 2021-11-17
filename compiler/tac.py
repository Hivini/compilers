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

    def _getOperatorString(self, nodeType: ASTTypes):
        if nodeType == ASTTypes.SUM:
            return '+'
        elif nodeType == ASTTypes.SUBSTRACT:
            return '-'
        elif nodeType == ASTTypes.MULTIPLICATION:
            return '*'
        elif nodeType == ASTTypes.DIVISION:
            return '/'
        elif nodeType == ASTTypes.EXPONENT:
            return '^'

    def _generateAlgebraTAC(self, node: ASTNode, currentLines: List[str]):
        if node.type == ASTTypes.INT_TO_FLOAT:
            innerNode = node.children[0]
            val = self._getNodeValue(innerNode)
            if innerNode.type in SemanticAnalyzer.algebraOp:
                val = self._generateAlgebraTAC(innerNode, currentLines)
            tmpVar = next(self.tmpGen)
            currentLines.append(f'{tmpVar} = int2float({val})')
            return tmpVar
        leftNode = node.children[0]
        rightNode = node.children[1]
        leftVar = self._getNodeValue(leftNode)
        rightVar = self._getNodeValue(rightNode)
        if leftNode.type in SemanticAnalyzer.algebraOp or leftNode.type == ASTTypes.INT_TO_FLOAT:
            leftVar = self._generateAlgebraTAC(leftNode, currentLines)
        if rightNode.type in SemanticAnalyzer.algebraOp or rightNode.type == ASTTypes.INT_TO_FLOAT:
            rightVar = self._generateAlgebraTAC(rightNode, currentLines)
        tmpVar = next(self.tmpGen)
        op = self._getOperatorString(node.type)
        currentLines.append(f'{tmpVar} = {leftVar} {op} {rightVar}')
        return tmpVar

    def _createDeclarationString(self, type: ASTTypes, name: str, value):
        if type == ASTTypes.INT_DCL:
            return f'int {name} = {value}'
        elif type == ASTTypes.FLOAT_DCL:
            return f'float {name} = {value}'
        elif type == ASTTypes.STRING_DCL:
            return f'string {name} = {value}'
        elif type == ASTTypes.BOOL_DCL:
            return f'bool {name} = {value}'

    def _generateTACHelper(self, node: ASTNode, currentLines: List[str]):
        if node.type in SemanticAnalyzer.declarationTypes:
            # Assign > First operation
            firstop = node.children[0].children[0]
            if firstop.type in SemanticAnalyzer.algebraOp or firstop.type == ASTTypes.INT_TO_FLOAT:
                tmpVar = self._generateAlgebraTAC(firstop, currentLines)
            else:
                tmpVar = self._getNodeValue(node)
            currentLines.append(self._createDeclarationString(
                node.type, node.variableName, tmpVar))
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
