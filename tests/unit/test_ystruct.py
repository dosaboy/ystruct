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

from .utils import BaseTestCase

from ystruct.ystruct import (
    YAMLDefOverrideBase,
    YAMLDefSection
)


class YAMLDefCustomerOverrideBase(YAMLDefOverrideBase):
    pass


class YAMLDefInput(YAMLDefCustomerOverrideBase):
    KEYS = ['input']


class YAMLDefMessage(YAMLDefOverrideBase):
    KEYS = ['message', 'message-alt']

    def __str__(self):
        return self.content


class YAMLDefMeta(YAMLDefOverrideBase):
    KEYS = ['meta']


class YAMLDefSettings(YAMLDefOverrideBase):
    KEYS = ['settings']


class TestYStruct(BaseTestCase):

    def test_struct(self):
        overrides = [YAMLDefInput, YAMLDefMessage, YAMLDefSettings,
                     YAMLDefMeta]
        with open('examples/checks.yaml') as fd:
            root = YAMLDefSection('fruit tastiness', yaml.safe_load(fd.read()),
                                  override_handlers=overrides)
            for leaf in root.leaf_sections:
                self.assertEqual(leaf.meta.category, 'tastiness')
                self.assertEqual(leaf.root.name, 'fruit tastiness')
                self.assertEqual(leaf.input.type, 'dict')
                if leaf.parent.name == 'apples':
                    if leaf.name == 'tasty':
                        self.assertEqual(str(leaf.message),
                                         'they make good cider.')
                        self.assertIsNone(leaf.message_alt, None)
                        self.assertEqual(leaf.input.value,
                                         {'color': 'red', 'crunchiness': 15})
                        self.assertEqual(leaf.settings.crunchiness,
                                         {'operator': 'ge', 'value': 10})
                        self.assertEqual(leaf.settings.color,
                                         {'operator': 'eq', 'value': 'red'})
                    else:
                        self.assertEqual(str(leaf.message),
                                         'default message')
                        self.assertIsNone(leaf.message_alt, None)
                        self.assertEqual(leaf.input.value,
                                         {'color': 'brown', 'crunchiness': 0})
                        self.assertEqual(leaf.settings.crunchiness,
                                         {'operator': 'le', 'value': 5})
                        self.assertEqual(leaf.settings.color,
                                         {'operator': 'eq', 'value': 'brown'})
                else:
                    self.assertEqual(str(leaf.message),
                                     'they make good juice.')
                    self.assertEqual(str(leaf.message_alt),
                                     'and good marmalade.')
                    self.assertEqual(leaf.input.value,
                                     {'acidity': 2, 'color': 'orange'})
                    self.assertEqual(leaf.settings.acidity,
                                     {'operator': 'lt', 'value': 5})
                    self.assertEqual(leaf.settings.color,
                                     {'operator': 'eq', 'value': 'red'})

    def test_empty_struct(self):
        overrides = [YAMLDefInput, YAMLDefMessage, YAMLDefSettings]
        root = YAMLDefSection('root', {}, override_handlers=overrides)
        for leaf in root.leaf_sections:
            self.assertEqual(leaf.input.type, 'dict')
