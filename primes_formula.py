def skip_whitespace(expression):
	if expression != "":
		while expression[0] in (' ', '\t', '\n'):
			expression = expression[1:]
	return expression

class Poly:
	operations = ["+", "-", "*", "/", "^"]
	operations_order = {"+": 0, "-": 0, "*": 1, "/": 1, "^": 2}

	def __init__(self, operation = None, var_name = None, constant = None):
		self.operation = operation
		self.var_name = var_name
		self.constant = constant
		self.child0 = None
		self.child1 = None
	def parse_value(expression):
		if expression[0].isnumeric():
			digit_char = len(expression)
			for i in range(len(expression)):
				if not expression[i].isnumeric():
					digit_char = i
					break
			return expression[digit_char:], Poly(None, None, expression[:digit_char])
		if expression[0].isalpha():
			alpha_char = len(expression)
			for i in range(len(expression)):
				if not expression[i].isalpha():
					alpha_char = i
					break
			return expression[alpha_char:], Poly(None, expression[:alpha_char], None)
		if expression[0] == "(":
			return Poly.parse(expression[1:])
	def parse_operation(expression):
		if expression != "" and expression[0] in Poly.operations:
			return Poly(expression[0], None, None)
	def parse_recursive(expression, order = -1):
		expression = skip_whitespace(expression)
		expression, value = Poly.parse_value(expression)
		old_expression = expression
		expression = skip_whitespace(expression)
		if expression == "" or expression[0] == ")":
			return expression, value
		operation = Poly.parse_operation(expression)

		while Poly.operations_order[operation.operation] > order:
			expression = skip_whitespace(expression[1:])
			expression, value2 = Poly.parse_recursive(expression, Poly.operations_order[operation.operation])
			operation.child0 = value
			operation.child1 = value2
			value = operation
			expression = skip_whitespace(expression)
			if expression == "" or expression[0] == ")":
				return expression, value
			operation = Poly.parse_operation(expression)
		return expression, value
	def parse(expression):
		expression = skip_whitespace(expression)
		expression, value = Poly.parse_value(expression)
		expression = skip_whitespace(expression)

		while expression != "" and expression[0] != ")":
			operation = Poly.parse_operation(expression)
			expression, value2 = Poly.parse_recursive(expression[1:], Poly.operations_order[operation.operation])
			operation.child0 = value
			operation.child1 = value2
			value = operation
			expression = skip_whitespace(expression)

		if expression != "" and expression[0] == ")":
			expression = expression[1:]

		return expression, value
	def to_str(self, var_translation = None):
		if self.constant:
			return self.constant
		if self.var_name:
			if var_translation and self.var_name in var_translation:
				return var_translation[self.var_name]
			else:
				return self.var_name
		if self.operation:
			return "(" + self.child0.to_str(var_translation) + self.operation + self.child1.to_str(var_translation) + ")"

primes_poly = """
(k + 2)*(1 -
(w*z + h + j - q)^2 -
((g*k + 2*g + k + 1)*(h + j) + h - z)^2 -
(16*(k + 1)^3*(k + 2)*(n + 1)^2 + 1 - f^2)^2 -
(2*n + p + q + z - e)^2 -
(e^3*(e + 2)*(a + 1)^2 + 1 - o^2)^2 -
((a^2 - 1)*y^2 + 1 - x^2)^2 -
(16*r^2*y^4*(a^2 - 1) + 1 - u^2)^2 -
(n + l + v - y)^2 -
((a^2 - 1)*l^2 + 1 - m^2)^2 -
(a*i + k + 1 - l - i)^2 -
(((a + u^2*(u^2 - a))^2 - 1)*(n + 4*d*y)^2 + 1 - (x + c*u)^2)^2 -
(p + l*(a - n - 1) + b*(2*a*n + 2*a - n^2 - 2*n - 2) - m)^2 -
(q + y*(a - p - 1) + s*(2*a*p + 2*a - p^2 - 2*p - 2) - x)^2 -
(z + p*l*(a - p) + t*(2*a*p - p^2 - 1) - p*m)^2"""

var_values = {"k": "k"}

def compute_index(index, num_indices):
	if num_indices == 1:
		return "n"
	elif num_indices%2 == 1 and index == 0:
		w = "floor((sqrt(8*n+1)-1)/2)"
		return "1/2*(" + w + "+3/2)^2-9/8-n"
	elif num_indices%2 == 1 and index != 0:
		child = compute_index(index - 1, num_indices - 1)
		w = "floor((sqrt(8*{0}+1)-1)/2)".format(child)
		return "{0}+1/8-1/2*({1}+1/2)^2".format(child, w)
	elif num_indices%2 == 0 and index < num_indices/2:
		child = compute_index(index, num_indices/2)
		w = "floor((sqrt(8*{0}+1)-1)/2)".format(child)
		return "1/2*({1}+3/2)^2-9/8-{0}".format(child, w)
	elif num_indices%2 == 0 and index >= num_indices/2:
		child = compute_index(index - num_indices/2, num_indices/2)
		w = "floor((sqrt(8*{0}+1)-1)/2)".format(child)
		return "{0}+1/8-1/2*({1}+1/2)^2".format(child, w)

def compute_sign(index):
	extract = compute_index(0, 27)
	if index == 0:
		return "(-1)^floor({0})".format(extract)
	else:
		return "(-1)^floor(({0})/{1})".format(extract, 2**index)

def set_variables():
	start = ord("a")
	for i in range(26):
		char = chr(start + i)
		abs_val = compute_index(i + 1, 27)
		if i < 10: # if the character comes before k
			j = i
		else:
			j = i - 1
		if i != 10: # if the character is not 'k'
			sign_val = compute_sign(j)
			value = "{0}*({1})".format(sign_val, abs_val)
		else:
			value = "({0})".format(abs_val)
		var_values[char] = value

def get_primes_formula():
	_, x = Poly.parse(primes_poly)
	indicator = x.to_str(var_values)
	return "floor(1/2*arctan({0})+7/8)*({1})+2".format(indicator, var_values["k"])

if __name__ == "__main__":
	set_variables()
	print(get_primes_formula())
