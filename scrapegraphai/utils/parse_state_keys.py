import re

def parse_expression(expression, state):
    # Check for empty expression
    if not expression:
        raise ValueError("Empty expression.")

    # Check for adjacent state keys without an operator between them
    pattern = r'\b(' + '|'.join(re.escape(key) for key in state.keys()) + r')(\b\s*\b)(' + '|'.join(re.escape(key) for key in state.keys()) + r')\b'
    if re.search(pattern, expression):
        raise ValueError("Adjacent state keys found without an operator between them.")

    # Remove spaces
    expression = expression.replace(" ", "")
    
    # Check for operators with empty adjacent tokens or at the start/end
    if expression[0] in '&|' or expression[-1] in '&|' or '&&' in expression or '||' in expression or '&|' in expression or '|&' in expression:
        raise ValueError("Invalid operator usage.")
    
    # Check for balanced parentheses and valid operator placement
    open_parentheses = close_parentheses = 0
    for i, char in enumerate(expression):
        if char == '(':
            open_parentheses += 1
        elif char == ')':
            close_parentheses += 1
        # Check for invalid operator sequences
        if char in "&|" and i + 1 < len(expression) and expression[i + 1] in "&|":
            raise ValueError("Invalid operator placement: operators cannot be adjacent.")
    
    # Check for missing or balanced parentheses
    if open_parentheses != close_parentheses:
        raise ValueError("Missing or unbalanced parentheses in expression.")

    # Helper function to evaluate an expression without parentheses
    def evaluate_simple_expression(exp):
        # Split the expression by the OR operator and process each segment
        for or_segment in exp.split('|'):
            # Check if all elements in an AND segment are in state
            and_segment = or_segment.split('&')
            if all(elem.strip() in state for elem in and_segment):
                return [elem.strip() for elem in and_segment if elem.strip() in state]
        return []

    # Helper function to evaluate expressions with parentheses
    def evaluate_expression(expression):
        while '(' in expression:
            start = expression.rfind('(')
            end = expression.find(')', start)
            sub_exp = expression[start + 1:end]
            # Replace the evaluated part with a placeholder and then evaluate it
            sub_result = evaluate_simple_expression(sub_exp)
            # For simplicity in handling, join sub-results with OR to reprocess them later
            expression = expression[:start] + '|'.join(sub_result) + expression[end+1:]
        return evaluate_simple_expression(expression)

    result = evaluate_expression(expression)
    
    if not result:
        raise ValueError("No state keys matched the expression.")

    # Remove redundant state keys from the result, without changing their order
    final_result = []
    for key in result:
        if key not in final_result:
            final_result.append(key)

    return final_result

expression = "user_input & (relevant_chunks | parsed_document | document)"
state = {
    "user_input": None,
    "document": None,
    "parsed_document": None,
    "relevant_chunks": None,
}

try:
    result = parse_expression(expression, state)
    print("Matched keys:", result)
except ValueError as e:
    print("Error:", e)
