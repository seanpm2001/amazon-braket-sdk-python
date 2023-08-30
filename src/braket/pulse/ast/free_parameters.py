# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from typing import Dict, Union

from openpulse import ast
from openqasm3.visitor import QASMTransformer
from oqpy import Program, float64
from oqpy.base import OQPyExpression

from braket.parametric.free_parameter_expression import FreeParameterExpression


class _FreeParameterExpressionIdentifier(ast.Identifier):
    """Dummy AST node with FreeParameterExpression instance attached"""

    def __init__(self, expression: FreeParameterExpression):
        super().__init__(name=f"FreeParameterExpression({expression})")
        self._expression = expression

    @property
    def expression(self) -> FreeParameterExpression:
        return self._expression


class _DurationFreeParameterExpression(OQPyExpression):
    def __init__(self, expression: FreeParameterExpression):
        self.name = f"({expression})"
        self.type = float64
        self._expression = expression

    def to_ast(self, program: Program = None) -> ast.Expression:
        return ast.Identifier(name=self.name)


class _FreeParameterTransformer(QASMTransformer):
    """Walk the AST and evaluate FreeParameterExpressions."""

    def __init__(self, param_values: Dict[str, float]):
        self.param_values = param_values
        super().__init__()

    def visit__FreeParameterExpressionIdentifier(
        self, identifier: ast.Identifier
    ) -> Union[_FreeParameterExpressionIdentifier, ast.FloatLiteral]:
        """Visit a FreeParameterExpressionIdentifier.
        Args:
            identifier (Identifier): The identifier.

        Returns:
            Union[_FreeParameterExpressionIdentifier, FloatLiteral]: The transformed expression.
        """
        new_value = identifier.expression.subs(self.param_values)
        if isinstance(new_value, FreeParameterExpression):
            return _FreeParameterExpressionIdentifier(new_value)
        else:
            return ast.FloatLiteral(new_value)
