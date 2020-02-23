"""
MIT License

Copyright (c) 2020 Nathan
Original available at https://github.com/courupteddata/StringBooleanExpression

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is a class that handles loading in a string and can parse passed in variables in the expression
This allows loading in a file that has boolean expressions.

Limitations:
In the event of a invalid string being found in the input_string a ValueError is raised.

"""

# Variable replacement
VARIABLE_START = "$"
FLOAT = ("F", "float")
INTEGER = ("I", "int")
STRING = ("S", "str")

# Operator
AND_OP = ("&&", " and ")
OR_OP = ("||", " or ")
NOT_OP = ("!!", " not ")

# Grouping, can't be changed as this isn't replaced just used a a reference
GROUP_OPEN = "("
GROUP_CLOSE = ")"

# Comparisons, change the left variable, the right one is what it maps to
COMPARISONS = [
    ("!=", " != "),  # Not Equal
    ("==",  " == "),  # Equal
    ("<<", " < "),  # Less than
    ("<=", " <= "),  # Less than Or Equal
    (">>", " > "),  # Greater Than
    (">=", " >= ")  # Greater Than or Equal
]

# Illegal characters and phrases that will cause ValueError exception to be thrown
ILLEGAL_STRINGS = ["import ", "eval", "\n", "\r", "\"", "\'",
                   "lambda", " if ", " else ", "for ", "def ",
                   "while", ":"]

# Used to wrap internal variables so they are unique
INTERNAL_VARIABLE_WRAP_CHAR = "__E__"


class StringBooleanExpression:
    def __init__(self, input_string: str, keyword_value_mapping=None):
        """
        NOTE: This can raise a ValueError in the event that the input_string was invalid.

        Initializes/Loads the string boolean expression that is represented as a string.
        The input string should have pieces of the format DataType$field_name[operator]value .
        For example: S$employee_name==BoB||F$salary<<20.5
                     This would return true if employee_name equals BoB or if the salary is less than 20.5

        :param input_string: The string that contains the
        :param keyword_value_mapping: Special keywords that will be replaced with certain values this can be used to
                                      compare with an empty string, since this is provided by the developer it
                                      is not scrubbed against ILLEGAL_STRINGS.
                                      By default there is EMPTY_STRING=""
        """
        if keyword_value_mapping is None:
            keyword_value_mapping = {"EMPTY_STRING": ""}

        self._check_for_invalid(input_string)
        self._command_string, self._variables = self._parse_input(input_string, keyword_value_mapping)

        self._sorted_variables = sorted(self._variables)
        print(self._command_string)
        self._command = self._set_up_function(self._command_string, self._sorted_variables)

    def check(self, input_dict: dict) -> bool:
        """
        If the input dictionary is missing the variables required to resolve the expression then False is returned
        :param input_dict: The dictionary to contain the fields to look for
        :return: If the expression resolves successfully then True, otherwise False (Also False if missing expression fields)
        """
        print(input_dict, self._sorted_variables)
        if all(variable in input_dict for variable in self._sorted_variables):
            return self._command(*[input_dict[item] for item in self._sorted_variables])
        else:
            return False

    @staticmethod
    def _set_up_function(command_string: str, sorted_variables: list):
        """
        This handles actually creating the command to run given a parsed command string and the sorted variables
        :param command_string: The parsed command string with the variables casted/replaced, and operators adjusted
        :param sorted_variables: The variables in their expected order
        :return: An evaluated expression that can be called given valid input
        """

        input_sequence = ", ".join([INTERNAL_VARIABLE_WRAP_CHAR + item + INTERNAL_VARIABLE_WRAP_CHAR
                                    for item in sorted_variables])
        command = eval("lambda " + input_sequence + ": " + command_string, {})
        print("lambda " + input_sequence + ": " + command_string)
        return command

    @staticmethod
    def _parse_input(input_string: str, keyword_value_map: dict) -> (str, set):
        """
        Parses the input based off of the comparisons
        :param input_string: A string that has already passed basic safety checks
        :param keyword_value_map: A map of reserved keywords that map to certain values
        :return: A string with the valid operators and the operators that have been corrected
        """

        # Handle comparisons first
        variables_hold = set()
        output = input_string
        for comparison in COMPARISONS:
            output, variables = StringBooleanExpression._handle_comparison(output, comparison[0], comparison[1],
                                                                           keyword_value_map)
            variables_hold.update(variables)

        output = output.replace(AND_OP[0], AND_OP[1])
        output = output.replace(OR_OP[0], OR_OP[1])
        output = output.replace(NOT_OP[0], NOT_OP[1])

        return output, variables_hold

    @staticmethod
    def _handle_comparison(input_string: str, comparison_operator: str, replacement: str,
                           keyword_value_map: dict) -> (str, set):
        """
        Splits based off of a comparison operator and the handles the left and right side of the operator
        :param input_string:
        :param comparison_operator: This would be index zero from and entry in COMPARISONS
        :param replacement: This would index one from and entry in COMPARISONS
        :param keyword_value_map: The map of certain keywords to replace with other values
        :return: Updated string and a set of the variables found
        """
        variables = set()

        parts = input_string.split(comparison_operator)

        if len(parts) == 1:
            return input_string, variables

        print(list(zip(range(0, len(parts) - 1), range(1, len(parts)))))
        for left_index, right_index in zip(range(0, len(parts) - 1), range(1, len(parts))):
            left_part = parts[left_index]
            right_part = parts[right_index]

            # Look right to left until end of string or open group or operator or variable start and then type
            left_item_length = 0
            left_value_length = 0
            previous_item = ""
            left_variable_type = ""
            left_is_variable = False
            for i in range(len(left_part) - 1, -1, -1):
                current_char = left_part[i]
                # open group case
                if current_char == GROUP_OPEN:
                    break
                if current_char + previous_item in {AND_OP[0], OR_OP[0], NOT_OP[0]}:
                    # Moving back one item because the previous item was incremented
                    left_item_length -= 1
                    left_value_length -= 1
                    break
                if previous_item == VARIABLE_START:
                    if current_char == STRING[0]:
                        left_variable_type = STRING[1]
                    elif current_char == FLOAT[0]:
                        left_variable_type = FLOAT[1]
                    elif current_char == INTEGER[0]:
                        left_variable_type = INTEGER[1]
                    else:
                        raise ValueError(f"Invalid type ({current_char}) for variable in {input_string}.")
                    left_item_length += 1
                    left_value_length -= 1
                    left_is_variable = True
                    break

                previous_item = current_char
                left_item_length += 1
                left_value_length += 1

            raw_left_value = left_part[-left_value_length:]


            left_value = StringBooleanExpression._wrap_string(raw_left_value, INTERNAL_VARIABLE_WRAP_CHAR,
                                                              left_is_variable)

            if left_is_variable:
                variables.add(raw_left_value)

            # Look left to right until end of string or close group or operator (flag variable start)
            right_item_length = 0
            right_value_start = 0
            right_value_stop = 0
            previous_item = ""
            right_variable_type = ""
            right_is_variable = False
            for i in range(len(right_part)):
                current_char = right_part[i]
                # open group case
                if current_char == GROUP_CLOSE:
                    break
                if previous_item + current_char in {AND_OP[0], OR_OP[0], NOT_OP[0]}:
                    # Moving back one item because the previous item was incremented
                    right_item_length -= 1
                    right_value_stop -= 1
                    break
                if current_char == VARIABLE_START:
                    if previous_item == STRING[0]:
                        right_variable_type = STRING[1]
                    elif previous_item == FLOAT[0]:
                        right_variable_type = FLOAT[1]
                    elif previous_item == INTEGER[0]:
                        right_variable_type = INTEGER[1]
                    else:
                        raise ValueError(f"Invalid type ({current_char}) for variable in {input_string}.")
                    right_value_start += 2
                    right_is_variable = True

                previous_item = current_char
                right_item_length += 1
                right_value_stop += 1
            raw_right_value = right_part[right_value_start: right_value_stop]
            right_value = StringBooleanExpression._wrap_string(raw_right_value,
                                                               INTERNAL_VARIABLE_WRAP_CHAR, right_is_variable)
            if right_is_variable:
                variables.add(raw_right_value)

            if right_variable_type == "" and left_variable_type == "":
                raise ValueError(f"Unknown value type for values (most likely a result of passing a "
                                 f"constant expression like 1==1): {left_value} and {right_value}")
            if right_variable_type == "":
                right_variable_type = left_variable_type
            if left_variable_type == "":
                left_variable_type = right_variable_type

            if right_variable_type != left_variable_type:
                raise ValueError(f"Type mismatch {left_variable_type} not comparable to {right_variable_type} "
                                 f"for values {left_value} and {right_value}")

            left_value = StringBooleanExpression._wrap_string(left_value, "\"", left_variable_type == STRING[1] and
                                                              not left_is_variable)
            right_value = StringBooleanExpression._wrap_string(right_value, "\"", right_variable_type == STRING[1]
                                                               and not right_is_variable)
            print(left_value, right_value)
            parts[left_index] = f"{left_part[:-left_item_length]} {left_variable_type}({left_value})"
            parts[right_index] = f"{right_variable_type}({right_value}) {right_part[right_value_stop:]}"

        return replacement.join(parts), variables

    @staticmethod
    def _wrap_string(value: str, wrap: str, condition: bool) -> str:
        """
        Given a condition this function will wrap a value
        :param value: The value to wrap
        :param wrap: The string to use to wrap the value
        :param condition: The condition to base the wrap logic off of
        :return: Either a wrapped string if condition is True, otherwise it just returns the input value
        """
        return (wrap if condition else "") + value + (wrap if condition else "")

    @staticmethod
    def _check_for_invalid(input_string: str) -> None:
        """
        Will check the input string for invalid strings that could be a sign of a malicious actor
        @param input_string: The command string to modify
        @return: None, but will raise a ValueError on something invalid being found
        """
        invalid_found = []
        for invalid in ILLEGAL_STRINGS:
            if invalid in input_string:
                invalid_found.append(f"\"{invalid}\"")

        if len(invalid_found) > 0:
            raise ValueError("Invalid strings found in parameter:" + ", ".join(invalid_found))
