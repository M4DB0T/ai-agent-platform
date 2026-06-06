import ast
import operator


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        operator_type = type(node.op)

        if operator_type not in ALLOWED_OPERATORS:
            raise ValueError("This operator is not allowed.")

        return ALLOWED_OPERATORS[operator_type](left, right)

    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        operator_type = type(node.op)

        if operator_type not in ALLOWED_OPERATORS:
            raise ValueError("This operator is not allowed.")

        return ALLOWED_OPERATORS[operator_type](operand)

    raise ValueError("Invalid expression.")


def calculate(expression: str) -> float:
    """
    Safely calculates a basic math expression.
    Supports +, -, *, /, ** and negative numbers.
    """

    try:
        parsed_expression = ast.parse(expression, mode="eval")
        result = _eval_node(parsed_expression.body)
        return result

    except Exception as error:
        raise ValueError(f"Calculation failed: {str(error)}")