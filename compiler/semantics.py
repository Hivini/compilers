from typing import List
from compiler.parser import ASTNode, ASTTypes, SymbolTable, Variable, VariableTypes


class SemanticError(Exception):
    pass


class SemanticAnalyzer:

    declarationTypes = [ASTTypes.INT_DCL, ASTTypes.FLOAT_DCL,
                        ASTTypes.STRING_DCL, ASTTypes.BOOL_DCL, ASTTypes.REASSIGN]
    algebraOp = [ASTTypes.SUM, ASTTypes.SUBSTRACT,
                 ASTTypes.MULTIPLICATION, ASTTypes.DIVISION, ASTTypes.EXPONENT, ASTTypes.UMINUS]
    comparisonOp = [ASTTypes.CMP_EQUAL, ASTTypes.CMP_NOT_EQUAL, ASTTypes.CMP_GREATER_EQUAL,
                    ASTTypes.CMP_LESS_EQUAL, ASTTypes.CMP_GREATER, ASTTypes.CMP_LESS]
    boolOp = [ASTTypes.AND_OP, ASTTypes.OR_OP]
    typeNodes = [ASTTypes.INT, ASTTypes.FLOAT, ASTTypes.STRING,
                 ASTTypes.BOOL_FALSE, ASTTypes.BOOL_TRUE]

    def __init__(self, root: ASTNode, progLines: List[str]) -> None:
        self.root = root
        self.progLines = progLines
        self.error = None

    def checkSemantics(self):
        self._checkSemanticsHelper(self.root)
        return self.root

    def _getReassingType(self, varType: VariableTypes):
        if varType == VariableTypes.INT:
            return ASTTypes.INT_DCL
        elif varType == VariableTypes.FLOAT:
            return ASTTypes.FLOAT_DCL
        elif varType == VariableTypes.STRING:
            return ASTTypes.STRING_DCL
        elif varType == VariableTypes.BOOL:
            return ASTTypes.BOOL_DCL

    def _checkSemanticsHelper(self, currentNode: ASTNode, symbolTable: SymbolTable = None):
        nodeType = currentNode.type
        if nodeType == ASTTypes.BLOCK:
            symbolTable = currentNode.symbolTable
        elif nodeType in self.declarationTypes:
            # Assign > Operations[]
            if len(currentNode.children) == 0:
                return
            baseOperation = currentNode.children[0].children[0]
            self._updateAlgebraNodeValues(baseOperation, symbolTable)
            newType = baseOperation.variableType
            newValue = baseOperation.variableValue
            if nodeType == ASTTypes.REASSIGN:
                # If no error it means it exists
                variable = self._searchVariableValue(
                    currentNode.variableName, symbolTable, currentNode.lineno)
                reassingType = self._getReassingType(variable.type)
                baseOperation = self._checkTypeAssignment(
                    baseOperation, reassingType, newType, currentNode.lineno, newValue)
                variable.value = baseOperation.variableValue
                self._updateVariableValue(
                    currentNode.variableName, variable, symbolTable, currentNode.lineno)
            else:
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
            if nodeType != ASTTypes.REASSIGN:
                symbolTable.table[currentNode.variableName].value = newValue
            return
        elif nodeType == ASTTypes.PRINT:
            base = currentNode.children[0]
            if base.type == ASTTypes.VARIABLE:
                variable = self._searchVariableValue(
                    base.variableName, symbolTable, currentNode.lineno)
                if variable.value == None:
                    self._addError(
                        f'Variable {base.variableName} has not been initialized', base.lineno)
                base.variableType = variable.type
                base.variableValue = variable.value
                currentNode.variableType = base.variableType
                currentNode.variableName = base.variableName
                currentNode.variableValue = base.variableValue
            self._updateAlgebraNodeValues(base, symbolTable)
        elif nodeType in SemanticAnalyzer.comparisonOp or nodeType in SemanticAnalyzer.boolOp:
            self._updateAlgebraNodeValues(currentNode, symbolTable)
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

    def _createInt2FloatNode(self, node: ASTNode):
        return ASTNode(ASTTypes.INT_TO_FLOAT, children=[node],
                       variableType=VariableTypes.FLOAT, variableValue=node.variableValue)

    def _updateAlgebraNodeValues(self, operation: ASTNode, symbolTable: SymbolTable):
        if not (operation.type in self.algebraOp or
                operation.type in self.comparisonOp or
                operation.type in self.boolOp):
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
            if resultVariable.value == None:
                self._addError(
                    f'Variable {leftNode.variableName} has not been initialized', leftNode.lineno)
            leftNode.variableType = resultVariable.type
            leftNode.variableValue = resultVariable.value
        if rightNode.type == ASTTypes.VARIABLE:
            resultVariable = self._searchVariableValue(
                rightNode.variableName, symbolTable, rightNode.lineno)
            rightNode.variableType = resultVariable.type
            rightNode.variableValue = resultVariable.value
            if resultVariable.value == None:
                self._addError(
                    f'Variable {rightNode.variableName} has not been initialized', rightNode.lineno)

        if operation.type in self.algebraOp:
            self._checkArithmeticOperation(
                leftNode, rightNode, operation.type, operation.lineno)
        elif operation.type in self.comparisonOp:
            self._checkComparisonOperation(
                leftNode, rightNode, operation.type, operation.lineno)
        elif operation.type in self.boolOp:
            self._checkBoolOperator(
                leftNode, rightNode, operation.type, operation.lineno)
        leftType = leftNode.variableType
        rightType = rightNode.variableType
        # Do the operation in the values
        if operation.type == ASTTypes.SUM:
            if leftType == VariableTypes.STRING or rightType == VariableTypes.STRING:
                operation.variableValue = str(
                    leftNode.variableValue) + str(rightNode.variableValue)
                operation.variableType = VariableTypes.STRING
            else:
                operation.variableType = VariableTypes.INT
                if leftType == VariableTypes.FLOAT or rightType == VariableTypes.FLOAT:
                    operation.variableType = VariableTypes.FLOAT
                if operation.variableType == VariableTypes.FLOAT and leftType == VariableTypes.INT:
                    leftNode = self._createInt2FloatNode(leftNode)
                    operation.children[0] = leftNode
                if operation.variableType == VariableTypes.FLOAT and rightType == VariableTypes.INT:
                    rightNode = self._createInt2FloatNode(rightNode)
                    operation.children[1] = rightNode
                operation.variableValue = leftNode.variableValue + rightNode.variableValue

        elif operation.type == ASTTypes.SUBSTRACT:
            operation.variableType = VariableTypes.INT
            if leftType == VariableTypes.FLOAT or rightType == VariableTypes.FLOAT:
                operation.variableType = VariableTypes.FLOAT
            if operation.variableType == VariableTypes.FLOAT and leftType == VariableTypes.INT:
                leftNode = self._createInt2FloatNode(leftNode)
                operation.children[0] = leftNode
            if operation.variableType == VariableTypes.FLOAT and rightType == VariableTypes.INT:
                rightNode = self._createInt2FloatNode(rightNode)
                operation.children[1] = rightNode
            operation.variableValue = leftNode.variableValue - rightNode.variableValue
        elif operation.type == ASTTypes.MULTIPLICATION:
            operation.variableType = VariableTypes.INT
            if leftType == VariableTypes.FLOAT or rightType == VariableTypes.FLOAT:
                operation.variableType = VariableTypes.FLOAT
            if operation.variableType == VariableTypes.FLOAT and leftType == VariableTypes.INT:
                leftNode = self._createInt2FloatNode(leftNode)
                operation.children[0] = leftNode
            if operation.variableType == VariableTypes.FLOAT and rightType == VariableTypes.INT:
                rightNode = self._createInt2FloatNode(rightNode)
                operation.children[1] = rightNode
            operation.variableValue = leftNode.variableValue * rightNode.variableValue
        elif operation.type == ASTTypes.DIVISION:
            operation.variableType = VariableTypes.INT
            if leftType == VariableTypes.FLOAT or rightType == VariableTypes.FLOAT:
                operation.variableType = VariableTypes.FLOAT
            if operation.variableType == VariableTypes.FLOAT and leftType == VariableTypes.INT:
                leftNode = self._createInt2FloatNode(leftNode)
                operation.children[0] = leftNode
            if operation.variableType == VariableTypes.FLOAT and rightType == VariableTypes.INT:
                rightNode = self._createInt2FloatNode(rightNode)
                operation.children[1] = rightNode
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
            if operation.variableType == VariableTypes.FLOAT and leftType == VariableTypes.INT:
                leftNode = self._createInt2FloatNode(leftNode)
                operation.children[0] = leftNode
            if operation.variableType == VariableTypes.FLOAT and rightType == VariableTypes.INT:
                rightNode = self._createInt2FloatNode(rightNode)
                operation.children[1] = rightNode
            operation.variableValue = pow(
                leftNode.variableValue, rightNode.variableValue)
        elif operation.type == ASTTypes.CMP_EQUAL:
            operation.variableType = VariableTypes.BOOL
            operation.variableValue = leftNode.variableValue == rightNode.variableValue
        elif operation.type == ASTTypes.CMP_NOT_EQUAL:
            operation.variableType = VariableTypes.BOOL
            operation.variableValue = leftNode.variableValue != rightNode.variableValue
        elif operation.type == ASTTypes.CMP_GREATER_EQUAL:
            operation.variableType = VariableTypes.BOOL
            operation.variableValue = leftNode.variableValue >= rightNode.variableValue
        elif operation.type == ASTTypes.CMP_LESS_EQUAL:
            operation.variableType = VariableTypes.BOOL
            operation.variableValue = leftNode.variableValue <= rightNode.variableValue
        elif operation.type == ASTTypes.CMP_GREATER:
            operation.variableType = VariableTypes.BOOL
            operation.variableValue = leftNode.variableValue > rightNode.variableValue
        elif operation.type == ASTTypes.CMP_LESS:
            operation.variableType = VariableTypes.BOOL
            operation.variableValue = leftNode.variableValue < rightNode.variableValue
        elif operation.type == ASTTypes.AND_OP:
            leftValue = leftNode.variableValue
            rightValue = rightNode.variableValue
            # This is done to perform operations like "0 and True"
            # in Python and return bool.
            if leftValue == 0:
                leftValue = False
            if rightValue == 0:
                rightValue = False
            operation.variableType = VariableTypes.BOOL
            operation.variableValue = leftValue and rightValue
        elif operation.type == ASTTypes.OR_OP:
            leftValue = leftNode.variableValue
            rightValue = rightNode.variableValue
            # This is done to perform operations like "0 and True"
            # in Python and return bool.
            if leftValue == 0:
                leftValue = False
            if rightValue == 0:
                rightValue = False
            operation.variableType = VariableTypes.BOOL
            operation.variableValue = leftValue or rightValue

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

    def _checkComparisonOperation(self, leftNode: ASTNode, rightNode: ASTNode, operation: ASTTypes, lineno: int):
        numTypes = [VariableTypes.INT, VariableTypes.FLOAT]
        leftType = leftNode.variableType
        rightType = rightNode.variableType
        leftValue = leftNode.variableValue
        rightValue = rightNode.variableValue
        areNumAndStrings = (leftType in numTypes and rightType == VariableTypes.STRING) or (
            rightType in numTypes and leftType == VariableTypes.STRING)
        areBoolsOrStrs = leftType == VariableTypes.BOOL or rightType == VariableTypes.BOOL or leftType == VariableTypes.STRING or rightType == VariableTypes.STRING
        if operation == ASTTypes.CMP_EQUAL:
            if areNumAndStrings:
                self._addError(
                    f'Cannot do "{leftValue}" == "{rightValue}". Mismatching types.', lineno)
        elif operation == ASTTypes.CMP_NOT_EQUAL:
            if areNumAndStrings:
                self._addError(
                    f'Cannot do "{leftValue}" != "{rightValue}". Mismatching types', lineno)
        elif operation == ASTTypes.CMP_GREATER_EQUAL:
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" >= "{rightValue}". Mismatching types', lineno)
        elif operation == ASTTypes.CMP_LESS_EQUAL:
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" <= "{rightValue}". Mismatching types', lineno)
        elif operation == ASTTypes.CMP_GREATER:
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" > "{rightValue}". Mismatching types', lineno)
        elif operation == ASTTypes.CMP_LESS:
            if areBoolsOrStrs:
                self._addError(
                    f'Cannot do "{leftValue}" < "{rightValue}". Mismatching types', lineno)

    def _checkBoolOperator(self, leftNode: ASTNode, rightNode: ASTNode, operation: ASTTypes, lineno: int):
        numTypes = [VariableTypes.INT, VariableTypes.FLOAT]
        leftType = leftNode.variableType
        rightType = rightNode.variableType
        leftValue = leftNode.variableValue
        rightValue = rightNode.variableValue
        areNumAndBools = (leftType in numTypes and rightType == VariableTypes.BOOL) or (
            rightType in numTypes and leftType == VariableTypes.BOOL)
        bothBools = (leftType == VariableTypes.BOOL and rightType ==
                     VariableTypes.BOOL)
        if not (areNumAndBools or bothBools):
            self._addError(
                f'Cannot perform boolean operation on "{leftValue}" and "{rightValue}"', lineno)

    def _searchVariableValue(self, name: str, symbolTable: SymbolTable, lineno: int) -> Variable:
        currentSymbolTable = symbolTable
        while currentSymbolTable != None:
            if name in currentSymbolTable.table:
                return currentSymbolTable.table[name]
            currentSymbolTable = currentSymbolTable.parent
        self._addError(f'Cannot find value {name} in any scope.', lineno)

    def _updateVariableValue(self, name: str, newValue: Variable, symbolTable: SymbolTable, lineno: int):
        currentSymbolTable = symbolTable
        while currentSymbolTable != None:
            if name in currentSymbolTable.table:
                currentSymbolTable.table[name] = newValue
                return
            currentSymbolTable = currentSymbolTable.parent
        self._addError(f'Cannot find value {name} in any scope.', lineno)

    def _addError(self, error: str, lineNumber: int = None):
        if lineNumber:
            error = f'{error}:\n\t{lineNumber})\t{self.progLines[lineNumber-1]}'
        self.error = error
        raise SemanticError('Semantic Error!')
