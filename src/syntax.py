"""
syntax.py: contains syntax for common languages
"""

syntax = {
    "py": {
        "keywords": ['False', 'await', 'else', 'import', 'pass',
                     'None', 'break', 'except', 'in', 'raise',
                     'True', 'class', 'finally', 'is', 'return',
                     'and', 'continue', 'for', 'lambda', 'try',
                     'as', 'def', 'from', 'nonlocal', 'while',
                     'assert', 'del', 'global', 'not', 'with',
                     'async', 'elif', 'if', 'or', 'yield'],
        "comment": '#'
    },
    "java": {
        "keywords": ['if', 'else', 'break', 'continue', 'while', 'do',
                     'for', 'double', 'long', 'int', 'float', 'String',
                     'System', 'print', 'println', 'boolean', 'byte',
                     'switch', 'case', 'catch', 'throw', 'throws',
                     'import', 'extends', 'class', 'public', 'return',
                     'try', 'short', 'super', 'this', 'char'],
        "comment": '/'
    },
    "c": {
        "keywords": ['auto', 'break', 'case', 'char', 'const', 'continue',
                     'default', 'do', 'double', 'else', 'enum', 'extern',
                     'float', 'for', 'goto', 'if', 'int', 'long', 'register',
                     'return', 'short', 'signed', 'sizeof', 'static',
                     'struct', 'switch', 'typedef', 'union', 'unsigned',
                     'void', 'volatile', 'while'],
        "comment": '//'
    }
}
