import unittest
import os
import json
from mirage.core.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_config_dir = os.path.join(os.path.expanduser('~'), '.mirage_test')
        self.test_config_file = os.path.join(self.test_config_dir, 'config.json')
        os.makedirs(self.test_config_dir, exist_ok=True)
        
        # Monkey patch the Config class to use our test directory
        Config.config_dir = self.test_config_dir
        Config.config_file = self.test_config_file
        
        self.config = Config()

    def tearDown(self):
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        os.rmdir(self.test_config_dir)

    def test_create_default_config(self):
        self.assertTrue(os.path.exists(self.test_config_file))
        with open(self.test_config_file, 'r') as f:
            config_data = json.load(f)
        self.assertIn('debug_mode', config_data)
        self.assertIn('log_level', config_data)
        self.assertIn('default_interface', config_data)

    def test_get_set_config(self):
        self.config.set('test_key', 'test_value')
        self.assertEqual(self.config.get('test_key'), 'test_value')

    def test_get_shortcuts(self):
        shortcuts = self.config.getShortcuts()
        self.assertIsInstance(shortcuts, dict)

    def test_data_exists(self):
        self.config.datas['test_module'] = {'TEST_ARG': 'test_value'}
        self.assertTrue(self.config.dataExists('test_module', 'TEST_ARG'))
        self.assertFalse(self.config.dataExists('test_module', 'NONEXISTENT_ARG'))

    def test_get_data(self):
        self.config.datas['test_module'] = {'TEST_ARG': 'test_value'}
        self.assertEqual(self.config.getData('test_module', 'TEST_ARG'), 'test_value')

if __name__ == '__main__':
    unittest.main()