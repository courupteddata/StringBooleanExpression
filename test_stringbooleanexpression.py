from unittest import TestCase
from stringbooleanexpression import StringBooleanExpression

class TestStringBooleanExpression(TestCase):

    def test_check(self):
        # Test the operators
        less_than = StringBooleanExpression("F$salary<<10")
        self.assertTrue(less_than.check({"salary": -10}), "Less than operator check")
        self.assertTrue(less_than.check({"salary": 1}), "Less than operator check")
        self.assertFalse(less_than.check({"salary": 10}), "Less than operator check")
        self.assertFalse(less_than.check({"salary": 100}), "Less than operator check")

        less_than_or_equal = StringBooleanExpression("F$salary<=10")
        self.assertTrue(less_than_or_equal.check({"salary": 1}), "Less than or equal operator check")
        self.assertTrue(less_than_or_equal.check({"salary": 10}), "Less than or equal operator check")
        self.assertFalse(less_than_or_equal.check({"salary": 100}), "Less than or equal operator check")

        greater_than = StringBooleanExpression("F$salary>>10")
        self.assertFalse(greater_than.check({"salary": 1}), "Greater than operator check")
        self.assertFalse(greater_than.check({"salary": 10}), "Greater than operator check")
        self.assertTrue(greater_than.check({"salary": 100}), "Greater than operator check")

        greater_than_or_equal = StringBooleanExpression("F$salary>=10")
        self.assertFalse(greater_than_or_equal.check({"salary": 1}), "Greater than or equal operator check")
        self.assertTrue(greater_than_or_equal.check({"salary": 10}), "Greater than or equal operator check")
        self.assertTrue(greater_than_or_equal.check({"salary": 100}), "Greater than or equal operator check")

        not_equal = StringBooleanExpression("F$salary!=10")
        self.assertTrue(not_equal.check({"salary": 1}), "Not equal operator check")
        self.assertFalse(not_equal.check({"salary": 10}), "Not equal operator check")
        self.assertTrue(not_equal.check({"salary": 100}), "Not equal operator check")

        equal = StringBooleanExpression("F$salary==10")
        self.assertFalse(equal.check({"salary": 1}), "Equal operator check")
        self.assertTrue(equal.check({"salary": 10}), "Equal operator check")
        self.assertFalse(equal.check({"salary": 100}), "Equal operator check")

        # Testing the check functionality
        simple_example = StringBooleanExpression("S$name==bob")
        self.assertFalse(simple_example.check({}), "An empty input should return false")
        self.assertFalse(simple_example.check({"name":""}), "Does not match expression requirement")
        self.assertTrue(simple_example.check({"name":"bob"}), "Matches simple condition")

        simple_reverse_example = StringBooleanExpression("bob==S$name")
        self.assertFalse(simple_reverse_example.check({}), "An empty input should return false")
        self.assertFalse(simple_reverse_example.check({"name":""}), "Does not match expression requirement")
        self.assertTrue(simple_reverse_example.check({"name":"bob"}), "Matches simple condition")


        complex_example = StringBooleanExpression("something with a space==S$name||(S$name==bob||jim==S$name||(EMPTY_STRING==S$name&&S$name==EMPTY_STRING&&F$salary>=10.5))")
        self.assertFalse(complex_example.check({"name":"", "salary":0}), "Checking complex false case")
        self.assertTrue(complex_example.check({"name":"", "salary":10.5}), "Checking complex true case")
        self.assertTrue(complex_example.check({"name": "", "salary": 1000}), "Checking complex true case")
        self.assertFalse(complex_example.check({"name": "", "salary": 0}), "Checking complex false case")
        self.assertTrue(complex_example.check({"name":"bob", "salary":0}), "Checking complex true case")
        self.assertTrue(complex_example.check({"name":"jim", "salary":0}), "Checking complex true case")
        self.assertTrue(complex_example.check({"name":"something with a space", "salary":0}), "Checking complex space true case")

    def test__set_up_function(self):
        # Testing the setup function
        variables = ["var_one", "var_two"]
        example_equal_expression = "var_one == var_two"

        function = StringBooleanExpression._set_up_function(example_equal_expression, variables, variable_wrap="")

        self.assertTrue(function("a", "a"))
        self.assertFalse(function("a", "b"))


    def test__parse_input(self):
        # Testing the parse function
        input_string = "S$var_one==var_two||S$var_one==TESTING"

        output_parsed_string, variables = StringBooleanExpression._parse_input(input_string, {"TESTING":"an example"})

        self.assertTrue("var_one" in variables)
        self.assertTrue("TESTING" not in variables)
        self.assertTrue("TESTING" not in output_parsed_string)
        self.assertTrue("an example" in output_parsed_string)

    def test__handle_comparison(self):
        # Testing handle comparison
        input_string = "S$var_one==var_two||S$var_one==TESTING"

        output_parsed_string, variables = StringBooleanExpression._handle_comparison(input_string, "==", "GARBAGE",
                                                                                     {"TESTING":"an example"})

        self.assertTrue("var_one" in variables)
        self.assertTrue("var_two" not in variables)
        self.assertTrue("==" not in output_parsed_string)
        self.assertTrue("GARBAGE" in output_parsed_string)
        self.assertTrue("an example" in output_parsed_string)
        self.assertTrue("TESTING" not in output_parsed_string)


    def test__wrap_string(self):
        wrap = "wrapping"
        not_wrapped = "value"
        expected_wrap = wrap + not_wrapped + wrap

        self.assertTrue(StringBooleanExpression._wrap_string(not_wrapped, wrap, True) == expected_wrap)
        self.assertTrue(StringBooleanExpression._wrap_string(not_wrapped, wrap, False) == not_wrapped)

    def test__check_for_invalid(self):
        invalid = "eval()"
        valid = "S$var_one==var_two||S$var_one==TESTING"

        try:
            StringBooleanExpression._check_for_invalid(invalid)
            self.fail("Failed to find invalid sequence in input")
        except ValueError:
            pass

        try:
            StringBooleanExpression._check_for_invalid(valid)
        except ValueError:
            self.fail("Incorrectly threw exception on valid string")