import importlib

GLOBAL_SETTINGS_MODULE = 'ninja_ide.core.conf.global_settings'


def load_settings():
    settings = {}
    module = importlib.import_module(GLOBAL_SETTINGS_MODULE)
    for setting in (s for s in dir(module) if not s.startswith('_')):
        value = getattr(module, setting)
        settings[setting] = value
    return settings
