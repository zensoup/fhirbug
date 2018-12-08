import unittest
from unittest.mock import Mock
from fhirball.config import utils
from .resources import sample_settings

utils.default_settings = sample_settings


class TestLazySettings(unittest.TestCase):

    def test_config_from_defaults(self):
        lazy_setting = utils.LazySettings()
        settings = lazy_setting._configure_from_defaults()
        self.assertIsInstance(settings, utils.FhirSettings)
        self.assertEquals(vars(settings), {'DEBUG': True, 'TESTING': True})

    def test_is_configured(self):
        lazy_setting = utils.LazySettings()
        self.assertFalse(lazy_setting.is_configured())
        lazy_setting._configure_from_defaults()
        self.assertTrue(lazy_setting.is_configured())

    def test_configure(self):
        class Mocked(utils.LazySettings):
            _configure_from_dict = Mock()
            _configure_from_path = Mock()
            _configure_from_defaults = Mock()

        lazy_setting = Mocked()

        test_settings = {'TEST': 5, 'SOME': 'OTHER', 'ignored': True}
        lazy_setting.configure(test_settings)
        lazy_setting._configure_from_dict.assert_called_once_with(test_settings)
        lazy_setting._configure_from_path.assert_not_called()
        lazy_setting._configure_from_defaults.assert_not_called()
