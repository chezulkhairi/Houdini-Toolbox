"""Test the ht.pyfilter.property module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import json
from mock import MagicMock, patch
import unittest

# Houdini Toolbox Imports
from ht.pyfilter import property as prop

reload(prop)

# =============================================================================
# CLASSES
# =============================================================================

class Test__parse_string_for_bool(unittest.TestCase):
    """Test ht.pyfilter.property._parse_string_for_bool."""

    def test_false(self):
        self.assertFalse(prop._parse_string_for_bool("False"))
        self.assertFalse(prop._parse_string_for_bool("false"))

    def test_true(self):
        self.assertTrue(prop._parse_string_for_bool("True"))
        self.assertTrue(prop._parse_string_for_bool("true"))

    def test_passthrough(self):
        self.assertEqual(
            prop._parse_string_for_bool("test"),
            "test"
        )


class Test__prep_value_to_set(unittest.TestCase):
    """Test ht.pyfilter.property._prep_value_to_set."""

    def test_None(self):
        result = prop._prep_value_to_set(None)

        self.assertEqual(result, [])

    def test_str(self):
        value = "value"

        result = prop._prep_value_to_set(value)

        self.assertEqual(result, [value])

    def test_unicode(self):
        value = u"value"

        result = prop._prep_value_to_set(value)

        self.assertEqual(result, [value])

    def test_dict(self):
        value = {
            "key1": "value1",
            "key2": "value2",
        }

        result = prop._prep_value_to_set(value)

        expected = json.dumps(value)

        self.assertEqual(result, [expected])

    def test_non_iterable(self):
        value = 123

        result = prop._prep_value_to_set(value)

        self.assertEqual(result, [value])

    def test_list_of_dicts(self):
        dict1 = {
            "key1": "value1",
            "key2": "value2",
        }

        value = [dict1]

        result = prop._prep_value_to_set(value)

        expected = json.dumps(dict1)

        self.assertEqual(result, [expected])

    @patch("ht.pyfilter.property.json.dumps")
    def test_list_of_dicts_TypeError(self, mock_dumps):
        mock_dumps.side_effect = TypeError
        dict1 = {
            "key1": "value1",
            "key2": "value2",
        }

        value = [dict1]

        result = prop._prep_value_to_set(value)

        self.assertEqual(result, value)

    @patch("ht.pyfilter.property.json.dumps")
    def test_list_of_dicts_ValueError(self, mock_dumps):
        mock_dumps.side_effect = ValueError
        dict1 = {
            "key1": "value1",
            "key2": "value2",
        }

        value = [dict1]

        result = prop._prep_value_to_set(value)

        self.assertEqual(result, value)

    def test_list_of_non_dicts(self):
        dict1 = {
            "key1": "value1",
            "key2": "value2",
        }

        value = [dict1, 3]

        result = prop._prep_value_to_set(value)

        self.assertEqual(result, value)


class Test__transform_values(unittest.TestCase):

    def test_None(self):
        result = prop._transform_values(None)

        self.assertIsNone(result)

    def test_single_json_string(self):
        expected = 123

        value = json.dumps(expected)

        result = prop._transform_values([value])

        self.assertEqual(result, expected)

    def test_single_string_json(self):
        expected = 123

        value = json.dumps(expected)

        result = prop._transform_values([value])

        self.assertEqual(result, expected)

    def test_single_string_non_json_dict(self):
        expected = {"comp1": "comp2", "comp3": "comp4"}

        result = prop._transform_values(["comp1 comp2 comp3 comp4"])

        self.assertEqual(result, expected)

    @patch("ht.pyfilter.property._parse_string_for_bool")
    def test_single_string_value(self, mock_parse):
        expected = "value"

        result = prop._transform_values([expected])

        self.assertEqual(result, mock_parse.return_value)

        mock_parse.assert_called_with(expected)

    def test_single_non_str(self):
        value = 123

        result = prop._transform_values([value])

        self.assertEqual(result, value)

    def test_multiple_json_values(self):
        values = [1, 2]

        result = prop._transform_values([str(val) for val in values])

        self.assertEqual(result, values)

    def test_multiple_non_json_values(self):
        values = [1, "2"]

        result = prop._transform_values(values)

        self.assertEqual(result, values)


class Test_get_property(unittest.TestCase):
    """Test ht.pyfilter.property.get_property."""

    def setUp(self):
        super(Test_get_property, self).setUp()

        self.mock_mantra = MagicMock()

        modules = {
            "mantra": self.mock_mantra,
        }

        self.module_patcher = patch.dict("sys.modules", modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    @patch("ht.pyfilter.property._transform_values")
    def test(self, mock_transform):
        mock_name = MagicMock(spec=str)

        result = prop.get_property(mock_name)

        self.assertEqual(
            result,
            mock_transform.return_value
        )

        mock_transform.assert_called_with(self.mock_mantra.property.return_value)


class Test_set_property(unittest.TestCase):
    """Test ht.pyfilter.property.set_property."""

    def setUp(self):
        super(Test_set_property, self).setUp()

        self.mock_mantra = MagicMock()

        modules = {
            "mantra": self.mock_mantra,
        }

        self.module_patcher = patch.dict("sys.modules", modules)
        self.module_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()

    @patch("ht.pyfilter.property._prep_value_to_set")
    def test(self, mock_prep):
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=int)

        prop.set_property(mock_name, mock_value)

        mock_prep.assert_called_with(mock_value)
        self.mock_mantra.setproperty.assert_called_with(mock_name, mock_prep.return_value)

# =============================================================================

if __name__ == '__main__':
    unittest.main()
