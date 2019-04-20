# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.


import logging
from logging.handlers import RotatingFileHandler
from ninja_ide import resources


LOG_FORMAT = "[%(asctime)s] [%(levelname)-6s]: %(name)-22s:%(funcName)-5s %(message)s"
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class CustomRotatingFileHandler(RotatingFileHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rotate file at each start of NINJA-IDE
        self.doRollover()


class _Logger:
    """General logger"""

    def __init__(self):
        self._level = logging.DEBUG
        self._loggers = {}

    def __call__(self, module_name: str):
        if module_name not in self._loggers:
            logger = logging.getLogger(module_name)
            self._loggers[module_name] = logger
        return self._loggers[module_name]

    def disable(self):
        for each_log in self._loggers.values():
            each_log.setLevel(logging.NOTSET)

    def set_level(self, level: int):
        self._level = level
        for each_log in self._loggers.values():
            each_log.setLevel(level)

    def set_up(self, verbose: bool):
        root_logger = logging.getLogger('ninja_ide')
        self._loggers['ninja_ide'] = root_logger
        handler = CustomRotatingFileHandler(
            resources.LOG_FILE_PATH, maxBytes=1e6, backupCount=10)
        root_logger.addHandler(handler)
        formatter = logging.Formatter(LOG_FORMAT, TIME_FORMAT)
        handler.setFormatter(formatter)
        self.set_level(self._level)
        if verbose:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            root_logger.addHandler(handler)


NinjaLogger = _Logger()
