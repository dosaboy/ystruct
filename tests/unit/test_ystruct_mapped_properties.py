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
from . import utils

from ystruct.ystruct import (
    YStructOverrideBase,
    YStructMappedOverrideBase,
    YStructSection
)


class YStructAssertionAttr(YStructOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['key', 'value1', 'value2', 'ops', 'message']

    @property
    def ops(self):
        return self.content


class YStructAssertion(YStructMappedOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['assertion']

    @classmethod
    def _override_mapped_member_types(cls):
        return [YStructAssertionAttr]


class YStructAssertionsBase(YStructMappedOverrideBase):

    @classmethod
    def _override_mapped_member_types(cls):
        return [YStructAssertion]


class YStructAssertionsLogicalOpt(YStructAssertionsBase):

    @classmethod
    def _override_keys(cls):
        return ['and', 'or', 'not']


class YStructAssertions(YStructAssertionsBase):

    @classmethod
    def _override_keys(cls):
        return ['assertions']

    @classmethod
    def _override_mapped_member_types(cls):
        return super()._override_mapped_member_types() + \
                    [YStructAssertionsLogicalOpt]


class TestYStructMappedProperties(utils.BaseTestCase):

    def test_mapping_single_member_full(self):
        """
        A single fully defined mapped property i.e. the principle property name
        is used rather than just its member(s).
        """
        content = {'assertions': {'assertion': {
                                    'key': 'key1',
                                    'value1': 1, 'value2': 2,
                                    'ops': ['gt'],
                                    'message': 'it failed'}}}

        root = YStructSection('mappingtest', content,
                              override_handlers=[YStructAssertions])
        checked = []
        for leaf in root.leaf_sections:
            checked.append(leaf.assertions._override_name)
            for assertion in leaf.assertions.members:
                self.assertEqual(len(assertion), 1)
                checked.append(assertion._override_name)
                for attrs in assertion:
                    checked.append(attrs.key)
                    self.assertEqual(attrs.key, 'key1')
                    self.assertEqual(attrs.value1, 1)
                    self.assertEqual(attrs.value2, 2)
                    self.assertEqual(attrs.ops, ['gt'])
                    self.assertEqual(attrs.message, 'it failed')

        self.assertEqual(checked, ['assertions', 'assertion', 'key1'])

    def test_mapping_single_member_short(self):
        """
        A single lazily defined mapped property i.e. the member property names
        are used rather than the principle.
        """
        content = {'assertions': {'key': 'key1', 'value1': 1, 'value2': 2,
                                  'ops': ['gt'],
                                  'message': 'it failed'}}

        root = YStructSection('mappingtest', content,
                              override_handlers=[YStructAssertions])
        checked = []
        for leaf in root.leaf_sections:
            checked.append(leaf.assertions._override_name)
            for assertion in leaf.assertions.members:
                self.assertEqual(len(assertion), 1)
                checked.append(assertion._override_name)
                for attrs in assertion:
                    checked.append(attrs.key)
                    self.assertEqual(attrs.key, 'key1')
                    self.assertEqual(attrs.value1, 1)
                    self.assertEqual(attrs.value2, 2)
                    self.assertEqual(attrs.ops, ['gt'])
                    self.assertEqual(attrs.message, 'it failed')

        self.assertEqual(checked, ['assertions', 'assertion', 'key1'])

    def test_mapping_list_members_partial(self):
        """
        A list of lazily defined properties. One with only a subset of members
        defined.
        """
        content = {'assertions': [{'key': 'key1',
                                   'value1': 1,
                                   'ops': ['gt'],
                                   'message': 'it failed'},
                                  {'key': 'key2',
                                   'value1': 3,
                                   'value2': 4,
                                   'ops': ['lt'],
                                   'message': 'it also failed'}]}

        root = YStructSection('mappingtest', content,
                              override_handlers=[YStructAssertions])
        checked = []
        for leaf in root.leaf_sections:
            checked.append(leaf.assertions._override_name)
            for assertion in leaf.assertions.members:
                self.assertEqual(len(assertion), 2)
                checked.append(assertion._override_name)
                for attrs in assertion:
                    checked.append(attrs.key)
                    if attrs.key == 'key1':
                        self.assertEqual(attrs.key, 'key1')
                        self.assertEqual(attrs.value1, 1)
                        self.assertEqual(attrs.value2, None)
                        self.assertEqual(attrs.ops, ['gt'])
                        self.assertEqual(attrs.message, 'it failed')
                    else:
                        self.assertEqual(attrs.key, 'key2')
                        self.assertEqual(attrs.value1, 3)
                        self.assertEqual(attrs.value2, 4)
                        self.assertEqual(attrs.ops, ['lt'])
                        self.assertEqual(attrs.message,
                                         'it also failed')

        self.assertEqual(checked, ['assertions', 'assertion', 'key1', 'key2'])

    def test_mapping_list_members_full(self):
        """
        A list of lazily defined properties. Both with all members defined.
        """
        content = {'assertions': [{'key': 'key1',
                                   'value1': 1,
                                   'value2': 2,
                                   'ops': ['gt'],
                                   'message': 'it failed'},
                                  {'key': 'key2',
                                   'value1': 3,
                                   'ops': ['lt'],
                                   'value2': 4,
                                   'message': 'it also failed'}]}

        root = YStructSection('mappingtest', content,
                              override_handlers=[YStructAssertions])
        checked = []
        for leaf in root.leaf_sections:
            checked.append(leaf.assertions._override_name)
            for assertion in leaf.assertions.members:
                self.assertEqual(len(assertion), 2)
                checked.append(assertion._override_name)
                for attrs in assertion:
                    checked.append(attrs.key)
                    if attrs.key == 'key1':
                        self.assertEqual(attrs.key, 'key1')
                        self.assertEqual(attrs.value1, 1)
                        self.assertEqual(attrs.value2, 2)
                        self.assertEqual(attrs.ops, ['gt'])
                        self.assertEqual(attrs.message, 'it failed')
                    else:
                        self.assertEqual(attrs.key, 'key2')
                        self.assertEqual(attrs.value1, 3)
                        self.assertEqual(attrs.value2, 4)
                        self.assertEqual(attrs.ops, ['lt'])
                        self.assertEqual(attrs.message,
                                         'it also failed')

        self.assertEqual(checked, ['assertions', 'assertion', 'key1', 'key2'])
