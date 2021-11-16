from typing import List
from compiler.parser import ASTNode, ASTTypes, SymbolTable, Variable, VariableTypes


class SemanticError(Exception):
    pass


class SemanticAnalyzer:

    declarationTypes = [ASTTypes.INT_DCL, ASTTypes.FLOAT_DCL,
                        ASTTypes.STRING_DCL, ASTTypes.BOOL_DCL]
    algebraOp = [ASTTypes.SUM, ASTTypes.SUBSTRACT,
                 ASTTypes.MULTIPLICATION, ASTTypes.DIVISION, ASTTypes.EXPONENT, ASTTypes.UMINUS]

    def __init__(self, root: ASTNode, progLines: List[str]) -> None:
        self.root = root
        self.progLines = progLines
        self.error = None

    def checkSemantics(self):
        self._checkSemanticsHelper(self.root)
        return self.root

    def _checkSemanticsHelper(self, currentNode: ASTNode, symbolTable: SymbolTable = None):
        nodeType = currentNode.type
        if nodeType == ASTTypes.BLOCK:
            symbolTable = currentNode.symbolTable
        elif nodeType in self.declarationTypes:
            # Assign > Operations[]
            baseOperation = currentNode.children[0].children[0]
            self._updateAlgebraNodeValues(baseOperation, symbolTable)
            newType = baseOperation.variableType
            newValue = baseOperation.variableValue
            # Get transformed value if it applies.
            baseOperation = self._checkTypeAssignment(
                baseOperation, currentNode.type, newType, currentNode.lineno, newValue)
            # In case of type changes update the variables.
            currentNode.children[0].children[0] = baseOperation
            newType = baseOperation.variableType
            newValue = baseOperation.variableValue
            currentNode.children[0].variableType = newType
            currentNode.children[0].variableValue = newValue
            currentNode.variableType = newType
            currentNode.variableValue = newValue
            symbolTable.table[currentNode.variableName].value = newValue
            return
        for c in currentNode.children:
            self._checkSemanticsHelper(c, symbolTable)

    def _checkTypeAssignment(self, node: ASTNode, dclType: ASTTypes, newType: VariableTypes, lineno: int, newValue):
        if dclType == ASTTypes.INT_DCL and newType != VariableTypes.INT:
            self._addError(
                f'Cannot assign {newType.name} to INT value', lineno)
        elif dclType == ASTTypes.FLOAT_DCL:
            if newType == VariableTypes.INT:
                node = ASTNode(ASTTypes.INT_TO_FLOAT, children=[node],
                               variableType=VariableTypes.FLOAT, variableValue=newValue)
            elif newType != VariableTypes.FLOAT:
                self._addError(
                    f'Cannot assign {newType.name} to FLOAT value', lineno)
        elif dclType == ASTTypes.STRING_DCL and newType != VariableTypes.STRING:
            self._addError(
                f'Cannot assign {newType.name} to STRING value', lineno)
        elif dclType == ASTTypes.BOOL_DCL and newType != VariableTypes.BOOL:
            self._addError(
                f'Cannot assign {newType.name} to BOOL value', lineno)
        return node

    def _updateAlgebraNodeValues(self, operation: ASTNode, symbolTable: SymbolTable):
        if operation.type not in self.algebraOp:
            return
        elif operation.type == ASTTypes.UMINUS:
            uminusnode = operation.children[0]
            if uminusnode.variableValue == None:
                self._updateAlgebraNodeValues(uminusnode, symbolTable)
            if uminusnode.variableType in [VariableTypes.BOOL, VariableTypes.STRING]:
                self._addError(
                    f'Invalid operation "-{uminusnode.variableValue}"', operation.lineno)
            operation.variableType = uminusnode.variableType
            operation.variableValue = -uminusnode.variableValue
            return
        leftNode = operation.children[0]
        rightNode = operation.children[1]
        # Having no value means that it needs to be calculated.
        if leftNode.variableValue == None:
            self._updateAlgebraNodeValues(leftNode, symbolTable)
        if rightNode.variableValue == None:
            self._updateAlgebraNodeValues(rightNode, symbolTable)
        if leftNode.type == ASTTypes.VARIABLE:
            resultVariable = self._searchVariableValue(
                leftNode.variableName, symbolTable, leftNode.lineno)
            leftNode.variableType = resultVariable.type
            leftNode.variableValue = resultVariable.value
        if rightNode.type == ASTTypes.VARIABLE:
            resultVariable = self._searchVariableValue(
                rightNode.variableName, symbolTable, rightNode.lineno)
            rightNode.variableType = resultVariable.type
            rightNode.variableValue = resultVariable.value

        self._checkArithmeticOperation(
            leftNode, rightNode, operation.type, operation.lineno)
        leftType = leftNode.variableType
        rightType = rightNode.variableType
        # Do the operation in the values
        if operation.type == ASTTypes.SUM:
            if leftType == VariableTypes.STRING or rightType == VariableTypes.STRING:
                operation.variableValue = str(
                    leftNode.variableValue) + str(rightNode.variableValue)
                operation.variableType = VariableTypes.STRING
                operation.type = ASTTypes.CONCATENATION
            else:
                operation.variableType = VariableTypes.INT
                if leftType == VariableTypes.FLOAT or rightType == VariableTypes.FLOAT:
                    operation.variableType = VariableTypes.FLOAT
                operation.variableValue = leftNode.variableValue + rightNode.variableValue
        elif operation.type == ASTTypes.SUBSTRACT:
            operation.variableType = VariableTypes.INT
            if leftType == VariableTypes.FLOAT or rightType == VariableTypes.FLOAT:
                operation.variableType = VariableTypes.FLOAT
            operation.variableValue = leftNode.variableValue - rightNode.variableValue
        elif operation.type == ASTTypes.MULTIPLICATION:
            operation.variableType = VariableTypes.INT
            if leftType == VariableTypes.FLOAT or rightType == VariableTypes.FLOAT:
                operation.variableType = VariableTypes.FLOAT
            operation.variableValue = leftNode.variableValue * rightNode.variableValue
        elif operation.type == ASTTypes.DIVISION:
            operation.variableType = VariableTypes.INT
            if leftType == VariableTypes.FLOAT or rightType == VariableTypes.FLOAT:
                operation.variableType = VariableTypes.FLOAT
            val = leftNode.variableValue / rightNode.variableValue
            if not val.is_integer():
                # We are going to check the final result during declaration
                if operation.variableType == VariableTypes.INT:
                    operation.variableType = VariableTypes.FLOAT
            else:
                val = int(val)
            operation.variableValue = val
        elif operation.type == ASTTypes.EXPONENT:
            operation.variableType = VariableTypes.INT
            if leftType == VariableTypes.FLOAT or rightType == VariableTypes.FLOAT or rightNode.variableValue < 0:
                operation.variableType = VariableTypes.FLOAT
            operation.variableValue = pow(
                leftNode.variableValue, rightNode.variableValue)

    def _checkArithmeticOperation(self, leftNode: ASTNode, rightNode: ASTNode, operation: ASTTypes, lineno: int):
        numTypes = [VariableTypes.INT, VariableTypes.FLOAT]
        leftType = leftNode.variableType
        rightType = rightNode.variableType
        leftValue = leftNode.variableValue
        rightValue = rightNode.variableValue
        bothAreNums = leftType in numTypes and rightType in numTypes
        if operation == ASTTypes.SUM:
            if leftType == VariableTypes.BOOL or rightType == VariableTypes.BOOL:
                self._addError(
                    f'Cannot sum values "{leftValue}" and "{rightValue}"', lineno)
        elif operation == ASTTypes.SUBSTRACT:
            if not(bothAreNums):
                self._addError(
                    f'Cannot substract values "{leftValue}" and "{rightValue}"', lineno)
        elif operation == ASTTypes.MULTIPLICATION:
            if not(bothAreNums):
                self._addError(
                    f'Cannot multiply values "{leftValue}" and "{rightValue}"', lineno)
        elif operation == ASTTypes.DIVISION:
            if not(bothAreNums):
                self._addError(
                    f'Cannot divide values "{leftValue}" and "{rightValue}"', lineno)
            elif rightValue == 0:
                self._addError(
                    f'{leftValue} / {rightValue} is invalid. Cannot perform division by zero', lineno)
        elif operation == ASTTypes.EXPONENT:
            if not(bothAreNums):
                self._addError(
                    f'Cannot get the exponent of "{leftValue}" ^ "{rightValue}"', lineno)

    def _searchVariableValue(self, name: str, symbolTable: SymbolTable, lineno: int) -> Variable:
        currentSymbolTable = symbolTable
        while currentSymbolTable != None:
            if name in currentSymbolTable.table:
                return currentSymbolTable.table[name]
            currentSymbolTable = currentSymbolTable.parent
        # This should happen btw since it was covered in the parser.
        self._addError(f'Cannot find value {name} in any scope.', lineno)

    def _addError(self, error: str, lineNumber: int = None):
        if lineNumber:
            error = f'{error}:\n\t{lineNumber})\t{self.progLines[lineNumber-1]}'
        self.error = error
        raise SemanticError('Semantic Error!')
