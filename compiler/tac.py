from typing import List
from compiler.parser import ASTNode, ASTTypes, VariableTypes
from compiler.semantics import SemanticAnalyzer


class TACProcessor:

    def __init__(self, astroot: ASTNode) -> None:
        self.astroot = astroot
        self.tmpGen = self._tempGenerator()
        self.labelGen = self._labelGenerator()

    def _tempGenerator(self) -> str:
        """Generates temporal variable names."""
        counter = 0
        while True:
            yield f"t{counter}"
            counter += 1

    def _labelGenerator(self) -> str:
        """Generates temporal labels."""
        counter = 0
        while True:
            yield f"L{counter}"
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
        elif nodeType == ASTTypes.CMP_EQUAL:
            return '=='
        elif nodeType == ASTTypes.CMP_NOT_EQUAL:
            return '!='
        elif nodeType == ASTTypes.CMP_GREATER_EQUAL:
            return '>='
        elif nodeType == ASTTypes.CMP_LESS_EQUAL:
            return '<='
        elif nodeType == ASTTypes.CMP_GREATER:
            return '>'
        elif nodeType == ASTTypes.CMP_LESS:
            return '<'
        elif nodeType == ASTTypes.AND_OP:
            return 'and'
        elif nodeType == ASTTypes.OR_OP:
            return 'or'

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
        if node.type == ASTTypes.VARIABLE:
            return self._getNodeValue(node)
        leftNode = node.children[0]
        rightNode = node.children[1]
        leftVar = self._getNodeValue(leftNode)
        rightVar = self._getNodeValue(rightNode)
        if leftNode.type == ASTTypes.STRING:
            leftVar = f'"{leftVar}"'
        if rightNode.type == ASTTypes.STRING:
            rightVar = f'"{rightVar}"'
        if leftNode.type in SemanticAnalyzer.algebraOp or leftNode.type == ASTTypes.INT_TO_FLOAT or \
                leftNode.type in SemanticAnalyzer.comparisonOp or leftNode.type in SemanticAnalyzer.boolOp:
            leftVar = self._generateAlgebraTAC(leftNode, currentLines)
        if rightNode.type in SemanticAnalyzer.algebraOp or rightNode.type == ASTTypes.INT_TO_FLOAT or \
                rightNode.type in SemanticAnalyzer.comparisonOp or rightNode.type in SemanticAnalyzer.boolOp:
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
            if firstop.type in SemanticAnalyzer.algebraOp or firstop.type == ASTTypes.INT_TO_FLOAT or \
                    firstop.type in SemanticAnalyzer.comparisonOp or firstop.type in SemanticAnalyzer.boolOp:
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
        elif node.type == ASTTypes.PRINT:
            printChild = node.children[0]
            if printChild.type in SemanticAnalyzer.algebraOp or printChild.type == ASTTypes.INT_TO_FLOAT or \
                    printChild.type in SemanticAnalyzer.comparisonOp or printChild.type in SemanticAnalyzer.boolOp:
                tmpVar = self._generateAlgebraTAC(printChild, currentLines)
            else:
                tmpVar = self._getNodeValue(printChild)
                if printChild.type == ASTTypes.STRING:
                    tmpVar = f'"{tmpVar}"'
            currentLines.append(f'print {tmpVar}')
        elif node.type == ASTTypes.IF_STATEMENT:
            # Get the if information
            ifNode = node.children[0]
            ifCondition = []
            condType = ifNode.children[0].type
            if condType in SemanticAnalyzer.comparisonOp or condType in SemanticAnalyzer.boolOp:
                ifVar = self._generateAlgebraTAC(
                    ifNode.children[0], ifCondition)
            else:
                ifCondVarValue = self._getNodeValue(ifNode.children[0])
                ifVar = next(self.tmpGen)
                ifCondition.append(f'{ifVar} = {ifCondVarValue}')
            # ifVar = self._generateAlgebraTAC(ifNode.children[0], ifCondition)
            ifBlockLines = []
            self._generateTACHelper(ifNode.children[1], ifBlockLines)
            # Define elements
            conditions = [ifCondition]
            conditionsVar = [ifVar]
            conditionLines = [ifBlockLines]
            conditionLabel = []
            for i in range(1, len(node.children)):
                currentNode = node.children[i]
                if currentNode.type == ASTTypes.ELSE:
                    conditionLabel.append(next(self.labelGen))
                    elseLines = []
                    self._generateTACHelper(currentNode.children[0], elseLines)
                    conditionLines.append(elseLines)
                # Process elifs
                else:
                    # Process condition
                    init = []
                    elifcondtype = currentNode.children[0].type
                    if elifcondtype in SemanticAnalyzer.comparisonOp or elifcondtype in SemanticAnalyzer.boolOp:
                        cvar = self._generateAlgebraTAC(
                            currentNode.children[0], init)
                    else:
                        elifCondVarValue = self._getNodeValue(
                            currentNode.children[0])
                        cvar = next(self.tmpGen)
                        init.append(f'{cvar} = {elifCondVarValue}')
                    # cvar = self._generateAlgebraTAC(
                    #     currentNode.children[0], init)
                    conditions.append(init)
                    conditionsVar.append(cvar)
                    # Create next label
                    conditionLabel.append(next(self.labelGen))
                    # Process block lines
                    elifLines = []
                    self._generateTACHelper(currentNode.children[1], elifLines)
                    conditionLines.append(elifLines)

            continueLabel = None
            if len(conditionLines) > 1:
                continueLabel = next(self.labelGen)
            else:
                conditionLabel.append(next(self.labelGen))
            for i in range(len(conditionLines)):
                # If it's in the end, it means it's an else
                if i == len(conditionLines) - 1 and len(conditionLines) > 1:
                    currentLines.extend(conditionLines[i])
                    continue
                conditionVar = next(self.tmpGen)
                currentLines.extend(conditions[i])
                currentLines.append(f'{conditionVar} = not {conditionsVar[i]}')
                currentLines.append(
                    f'{conditionVar} IFGOTO {conditionLabel[i]}')
                currentLines.extend(conditionLines[i])
                if len(conditionLines) > 1:
                    currentLines.append(f'GOTO {continueLabel}')
                currentLines.append(f'LABEL {conditionLabel[i]}')
            if continueLabel != None:
                currentLines.append(f'LABEL {continueLabel}')
        elif node.type == ASTTypes.WHILE_STATEMENT:
            condType = node.children[0].type
            whileCondition = []
            if condType in SemanticAnalyzer.comparisonOp or condType in SemanticAnalyzer.boolOp or condType == ASTTypes.VARIABLE:
                whileVar = self._generateAlgebraTAC(
                    node.children[0], whileCondition)
            else:
                whileVarValue = self._getNodeValue(node.children[0])
                whileVar = next(self.tmpGen)
                whileCondition.append(f'{whileVar} = {whileVarValue}')
            whileStartLabel = next(self.labelGen)
            whileBlockLines = []
            self._generateTACHelper(node.children[1], whileBlockLines)
            whileEndLabel = next(self.labelGen)
            # Start the while loop
            forCondTmp = next(self.tmpGen)
            currentLines.append(f'LABEL {whileStartLabel}')
            currentLines.extend(whileCondition)
            currentLines.append(f'{forCondTmp} = not {whileVar}')
            currentLines.append(f'{forCondTmp} IFGOTO {whileEndLabel}')
            # While body
            currentLines.extend(whileBlockLines)
            # End of while
            currentLines.append(f'GOTO {whileStartLabel}')
            currentLines.append(f'LABEL {whileEndLabel}')
        elif node.type == ASTTypes.FOR_STATEMENT:
            forVar = node.children[0]
            forCond = node.children[1]
            forUpdate = node.children[2]
            forBlock = node.children[3]
            forStartLabel = next(self.labelGen)
            # Create the variable declaration lines.
            forVarLines = []
            self._generateTACHelper(forVar, forVarLines)
            # Create the conditional lines.
            forCondLines = []
            condType = forCond.type
            if condType in SemanticAnalyzer.comparisonOp or condType in SemanticAnalyzer.boolOp:
                forCondVar = self._generateAlgebraTAC(
                    forCond, forCondLines)
            else:
                forCondVarValue = self._getNodeValue(forCond)
                forCondVar = next(self.tmpGen)
                forCondLines.append(f'{forCondVar} = {forCondVarValue}')
            # Create the reassign lines.
            forUpdateLines = []
            self._generateTACHelper(forUpdate, forUpdateLines)
            # Create the body lines.
            forBlockLines = []
            self._generateTACHelper(forBlock, forBlockLines)
            # Create the TAC lines.
            forEndLabel = next(self.labelGen)
            forCondTmp = next(self.tmpGen)
            currentLines.extend(forVarLines)
            currentLines.append(f'LABEL {forStartLabel}')
            currentLines.extend(forCondLines)
            currentLines.append(f'{forCondTmp} = not {forCondVar}')
            currentLines.append(f'{forCondTmp} IFGOTO {forEndLabel}')
            currentLines.extend(forBlockLines)
            currentLines.extend(forUpdateLines)
            currentLines.append(f'GOTO {forStartLabel}')
            currentLines.append(f'LABEL {forEndLabel}')
        else:
            for c in node.children:
                self._generateTACHelper(c, currentLines)

    def generateTAC(self):
        lines = []
        self._generateTACHelper(self.astroot, lines)
        return lines
