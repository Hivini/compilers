from typing import List
from compiler.parser import ASTNode, ASTTypes, VariableTypes
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
            currentLines.append(f'{tmpVar} = toFloat {val}')
            return tmpVar
        if node.type == ASTTypes.UMINUS:
            innerNode = node.children[0]
            val = self._getNodeValue(innerNode)
            if innerNode.type in SemanticAnalyzer.algebraOp or innerNode.type == ASTTypes.INT_TO_FLOAT:
                val = self._generateAlgebraTAC(innerNode, currentLines)
            tmpVar = next(self.tmpGen)
            currentLines.append(f'{tmpVar} = -{val}')
            return tmpVar
        leftNode = node.children[0]
        rightNode = node.children[1]
        leftVar = self._getNodeValue(leftNode)
        rightVar = self._getNodeValue(rightNode)
        if leftNode.type == ASTTypes.STRING:
            leftVar = f'"{leftVar}"'
        if rightNode.type == ASTTypes.STRING:
            rightVar = f'"{rightVar}"'
        if leftNode.type in SemanticAnalyzer.algebraOp or leftNode.type == ASTTypes.INT_TO_FLOAT:
            leftVar = self._generateAlgebraTAC(leftNode, currentLines)
        if rightNode.type in SemanticAnalyzer.algebraOp or rightNode.type == ASTTypes.INT_TO_FLOAT:
            rightVar = self._generateAlgebraTAC(rightNode, currentLines)
        tmpVar = next(self.tmpGen)
        op = self._getOperatorString(node.type)
        currentLines.append(f'{tmpVar} = {leftVar} {op} {rightVar}')
        return tmpVar

    def _getDclTypeString(self, type: VariableTypes):
        if type == VariableTypes.INT:
            return 'declareint'
        elif type == VariableTypes.FLOAT:
            return 'declarefloat'
        elif type == VariableTypes.STRING:
            return 'declarestring'
        elif type == VariableTypes.BOOL:
            return 'declarebool'

    def _createDeclarationLines(self, type: VariableTypes, name: str, value):
        lines = []
        lines.append(f'{self._getDclTypeString(type)} {name}')
        lines.append(f'{name} = {value}')
        return lines

    def _generateTACHelper(self, node: ASTNode, currentLines: List[str]):
        if node.type in SemanticAnalyzer.declarationTypes:
            # Assign > First operation
            if len(node.children) == 0:
                currentLines.append(
                    f'{self._getDclTypeString(node.variableType)} {node.variableName}')
                return
            firstop = node.children[0].children[0]
            if firstop.type in SemanticAnalyzer.algebraOp or firstop.type == ASTTypes.INT_TO_FLOAT:
                tmpVar = self._generateAlgebraTAC(firstop, currentLines)
            else:
                tmpVar = self._getNodeValue(node)
                if firstop.type == ASTTypes.STRING:
                    tmpVar = f'"{tmpVar}"'
            if node.type == ASTTypes.REASSIGN:
                currentLines.append(f'{node.variableName} = {tmpVar}')
            else:
                currentLines.extend(self._createDeclarationLines(
                    node.variableType, node.variableName, tmpVar))
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
