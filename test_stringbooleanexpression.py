from unittest import TestCase
from stringbooleanexpression import StringBooleanExpression

class TestStringBooleanExpression(TestCase):

    def test_check(self):
        # Testing the check functionality
        """
        simple_example = StringBooleanExpression("S$name==bob")
        self.assertFalse(simple_example.check({}), "An empty input should return false")
        self.assertFalse(simple_example.check({"name":""}), "Does not match expression requirement")
        self.assertTrue(simple_example.check({"name":"bob"}), "Matches simple condition")

        simple_reverse_example = StringBooleanExpression("bob==S$name")
        self.assertFalse(simple_reverse_example.check({}), "An empty input should return false")
        self.assertFalse(simple_reverse_example.check({"name":""}), "Does not match expression requirement")
        self.assertTrue(simple_reverse_example.check({"name":"bob"}), "Matches simple condition")
        """

        complex_example = StringBooleanExpression("S$name==bob||S$name==jim||=S$name")


    def test__set_up_function(self):
        self.fail()

    def test__parse_input(self):
        self.fail()

    def test__handle_comparison(self):
        self.fail()

    def test__wrap_string(self):
        self.fail()

    def test__check_for_invalid(self):
        self.fail()
