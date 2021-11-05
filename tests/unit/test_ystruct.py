# Copyright 2021 Edward Hope-Morley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import yaml

from utils import BaseTestCase

from ystruct.ystruct import (
    YAMLDefOverrideBase,
    YAMLDefSection
)


class YAMLDefCustomerOverrideBase(YAMLDefOverrideBase):
    pass


class YAMLDefInput(YAMLDefCustomerOverrideBase):
    KEY = 'input'


class YAMLDefMessage(YAMLDefOverrideBase):
    KEY = 'message'


class YAMLDefSettings(YAMLDefOverrideBase):
    KEY = 'settings'


class TestYStruct(BaseTestCase):

    def test_struct(self):
        overrides = [YAMLDefInput, YAMLDefMessage, YAMLDefSettings]
        with open('examples/checks.yaml') as fd:
            root = YAMLDefSection('root', yaml.safe_load(fd.read()),
                                  override_handlers=overrides)
            for leaf in root.leaf_sections:
                self.assertEquals(leaf.input.type, 'dict')
                if leaf.parent.name == 'apples':
                    self.assertEquals(leaf.input.value,
                                      {'color': 'red', 'crunchiness': 15})
                    self.assertEquals(leaf.settings.crunchiness,
                                      {'operator': 'ge', 'value': 10})
                    self.assertEquals(leaf.settings.color,
                                      {'operator': 'eq', 'value': 'red'})
                else:
                    self.assertEquals(leaf.input.value,
                                      {'acidity': 2, 'color': 'orange'})
                    self.assertEquals(leaf.settings.acidity,
                                      {'operator': 'lt', 'value': 5})
                    self.assertEquals(leaf.settings.color,
                                      {'operator': 'eq', 'value': 'red'})
