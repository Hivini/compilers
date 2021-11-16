from compiler.parser import ASTTypes


class SemanticError(Exception):
    pass


class SemanticAnalyzer:

    def __init__(self, root: ASTTypes) -> None:
        self.root = root
