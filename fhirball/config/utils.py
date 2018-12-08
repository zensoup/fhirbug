import importlib

from fhirball.exceptions import ConfigurationError
from fhirball.config import default_settings


class FhirSettings:
    """
    A simple namespace class to hold the settings.
    """

    pass


class LazySettings:
    """
    A lazy object containing the project's settings.

    Instances of this class will not import any settings modules on import
    and instead will wait until the first time they are accessed.

    This is loosely based on the LazyObject used by django for their settings.
    """

    _wrapped = None

    def configure(self, config=None):
        """
        Configuration wrapper. Accept a dictionary or string and pass it on to :func:`configure_from_dict` or :func:`configure_from_path`
        """
        if config is None:
            settings = self._configure_from_defaults()
            self._wrapped = settings
        if isinstance(config, str):
            return self._configure_from_path(config)
        if isinstance(config, dict):
            return self._configure_from_dict(config)
        raise ConfigurationError(
            "Invalid configuration object, you must provide a dict or string representing the path to a configuration file"
        )

    def __getattr__(self, name):
        if self._wrapped is None:
            self.configure()
        return getattr(self._wrapped, name)

    def __setattr__(self, name, value):
        if name == '_wrapped':
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__["_wrapped"] = value
            return
        if self._wrapped is None:
            self.configure()
        setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        if self._wrapped is None:
            self.configure()
        delattr(self._wrapped, name)

    def _configure_from_defaults(self):
        """
        Load the default settings defined in :module:`fhirball.config.default_settings`.
        This method does not set the ``_wrapped`` attribute because is also called from
        the other configuration methods, so the returned objects must be assigned to
        ``self_wrapped`` manually.
        """
        settings = FhirSettings()
        for setting in dir(default_settings):
            if setting.isupper():
                setting_value = getattr(default_settings, setting)
                setattr(settings, setting, setting_value)
        self._wrapped = settings
        return settings

    def _configure_from_path(self, path):
        """
        Read a path to a module and import all viariables defined inside it
        as the project settings
        """
        if self._wrapped is not None:
            raise ConfigurationError(
                "Settings have already been configured. You either called configure twice or are trying to configure the settings after they have already been accessed. If you suspect the latter, try configuring the settings earlier in your application's lifecycle."
            )

        settings = self._configure_from_defaults()
        settings_module = importlib.import_module(path)
        for key in dir(settings_module):
            if key.isupper():
                setattr(settings, key, getattr(settings_module, key))
        self._wrapped = settings
        return settings

    def _configure_from_dict(self, dict):
        """
        Read a dictionary and load it as project settings.
        """
        if self._wrapped is not None:
            raise ConfigurationError(
                "Settings have already been configured. You either called configure twice or are trying to configure the settings after they have already been accessed. If you suspect the latter, try configuring the settings earlier in your application's lifecycle."
            )

        settings = self._configure_from_defaults()
        for key, value in dict.items():
            if key.isupper():
                setattr(settings, key, value)
        self._wrapped = settings
        return settings

    def is_configured(self):
        """
        Return True if the settings have been initialized, False if they haven't

        :returns: bool
        """
        return self._wrapped is not None

    def _reset(self):
        """
        Delete the wrapped settings object. No good things will come from this.
        DO NOT use this in productions, it's intended for testing only.
        """
        self._wrapped = None
