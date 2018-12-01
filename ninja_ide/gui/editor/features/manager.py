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

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)

# TODO: documentation


class UnknownFeatureError(Exception):
    pass


class FeatureManager:
    """Class to handle editor Features"""

    def __init__(self, editor):
        self._editor = editor
        self._features = {}

    def install(self, feature_class):
        logger.info('Installing feature: %s', feature_class.__name__)
        feature_instance = feature_class()
        self._features[feature_instance.__class__.__name__] = feature_instance
        feature_instance.register(self._editor)
        return feature_instance

    def uninstall(self, class_or_name):
        if not isinstance(class_or_name, str):
            class_or_name = class_or_name.__name__
        feature = self.get(class_or_name)
        logger.debug('Uninstalling feature "%s"', class_or_name)
        feature.unregister()
        del self._features[class_or_name]

    def get(self, class_or_name):
        if not isinstance(class_or_name, str):
            class_or_name = class_or_name.__name__
        feature = self._features.get(class_or_name)
        if feature is None:
            logger.error('"%s" Feature doesn\'t exists', class_or_name)
            raise UnknownFeatureError('%s' % class_or_name)
        return feature

    def clear(self):
        for feature in self:
            self.uninstall(feature.__class__.__name__)

    def __len__(self):
        return len(self._features)

    def __iter__(self):
        return iter([feature for feature in self._features.values()])
