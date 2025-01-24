import unittest
from unittest.mock import Mock, patch

from lox.lox_class import LoxClass
from lox.lox_function import LoxFunction
from lox.lox_instance import LoxInstance


class TestLoxClass(unittest.TestCase):
    def setUp(self):
        self.interpreter = Mock()
        self.empty_methods = {}
        self.base_class = LoxClass(None, "Base", None, self.empty_methods)

    def test_class_creation(self):
        test_class = LoxClass(None, "Test", None, self.empty_methods)
        self.assertEqual(str(test_class), "Test")
        self.assertEqual(test_class.arity(), 0)

    def test_instance_creation(self):
        test_class = LoxClass(None, "Test", None, self.empty_methods)
        instance = test_class.call(self.interpreter, [])
        self.assertIsInstance(instance, LoxInstance)
        self.assertEqual(instance.klass, test_class)

    def test_method_finding(self):
        mock_method = Mock(spec=LoxFunction)
        methods = {"test_method": mock_method}
        test_class = LoxClass(None, "Test", None, methods)

        found_method = test_class.find_method("test_method")
        self.assertEqual(found_method, mock_method)

        not_found = test_class.find_method("nonexistent")
        self.assertIsNone(not_found)

    def test_inheritance(self):
        parent_method = Mock(spec=LoxFunction)
        parent_methods = {"parent_method": parent_method}
        parent_class = LoxClass(None, "Parent", None, parent_methods)

        child_method = Mock(spec=LoxFunction)
        child_methods = {"child_method": child_method}
        child_class = LoxClass(None, "Child", parent_class, child_methods)

        self.assertEqual(child_class.find_method("parent_method"), parent_method)
        self.assertEqual(child_class.find_method("child_method"), child_method)
        self.assertIsNone(child_class.find_method("nonexistent"))

    def test_method_override(self):
        parent_method = Mock(spec=LoxFunction)
        child_method = Mock(spec=LoxFunction)

        parent_methods = {"test": parent_method}
        child_methods = {"test": child_method}

        parent_class = LoxClass(None, "Parent", None, parent_methods)
        child_class = LoxClass(None, "Child", parent_class, child_methods)

        self.assertEqual(child_class.find_method("test"), child_method)

    def test_initializer(self):
        init_method = Mock(spec=LoxFunction)
        init_method.arity.return_value = 2
        bound_method = Mock(spec=LoxFunction)
        init_method.bind.return_value = bound_method

        methods = {"init": init_method}
        test_class = LoxClass(None, "Test", None, methods)

        self.assertEqual(test_class.arity(), 2)

        args = [1, 2]
        instance = test_class.call(self.interpreter, args)

        init_method.bind.assert_called_once_with(instance)
        bound_method.call.assert_called_once_with(self.interpreter, args)

    def test_metaclass(self):
        metaclass = Mock(spec=LoxClass)
        test_class = LoxClass(metaclass, "Test", None, self.empty_methods)
        self.assertEqual(test_class.klass, metaclass)


if __name__ == "__main__":
    unittest.main()
