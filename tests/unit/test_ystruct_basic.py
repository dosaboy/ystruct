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

from collections import UserString

from . import utils

from structr import (
    StructROverrideBase,
    StructRMappedOverrideBase,
    StructROverrideRawType,
    StructRSection,
)
from structr.structr import MappedOverrideState


class StructRStrProp(StructROverrideBase, UserString):

    @classmethod
    def _override_keys(cls):
        return ['strprop']

    @property
    def data(self):
        return self.content


class StructRDictProp(StructROverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['dictprop']


class StructRPropGroup(StructRMappedOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['pgroup']

    @classmethod
    def _override_mapped_member_types(cls):
        return [StructRStrProp, StructRDictProp, StructROverrideRawType]


class TestStructRSimpleProps(utils.BaseTestCase):

    def test_struct_simple_prop_single(self):
        overrides = [StructRStrProp]
        _yaml = """
        strprop: myval
        """
        root = StructRSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.strprop), StructRStrProp)
            self.assertEqual(leaf.strprop, "myval")

    def test_struct_simple_prop_multi(self):
        overrides = [StructRStrProp]
        _yaml = """
        s1:
          strprop: myval1
        s2:
          strprop: myval2
        """
        root = StructRSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.strprop), StructRStrProp)
            if leaf.name == 's1':
                self.assertEqual(leaf.strprop, "myval1")
            else:
                self.assertEqual(leaf.strprop, "myval2")

    def test_struct_simple_prop_single_list(self):
        overrides = [StructRStrProp]
        _yaml = """
        - strprop: myval1
        - strprop: myval2
        """
        root = StructRSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        vals = []
        for leaf in root.leaf_sections:
            for prop in leaf.strprop:
                self.assertEqual(type(prop), StructRStrProp)
                vals.append(prop)

            self.assertEqual(vals, ["myval1", "myval2"])


class TestStructRMappedProps(utils.BaseTestCase):

    def test_struct_mapped_prop_single(self):
        overrides = [StructRPropGroup]
        _yaml = """
        pgroup:
          strprop: myval
        """
        root = StructRSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.pgroup), StructRPropGroup)
            self.assertEqual(len(leaf.pgroup), 1)
            for pgroup in leaf.pgroup:
                self.assertEqual(len(pgroup), 1)
                self.assertEqual(type(pgroup.strprop), str)
                self.assertEqual(pgroup.strprop, "myval")

    def test_struct_mapped_prop_single_list(self):
        overrides = [StructRPropGroup]
        _yaml = """
        pgroup:
          - '1'
          - '2'
          - '3'
        """
        root = StructRSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        vals = []
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.pgroup), StructRPropGroup)
            self.assertEqual(len(leaf.pgroup), 1)
            for pgroup in leaf.pgroup:
                self.assertEqual(type(pgroup), MappedOverrideState)
                members = 0
                self.assertEqual(len(pgroup), 3)
                for member in pgroup:
                    self.assertEqual(type(member), StructROverrideRawType)
                    members += 1
                    vals.append(str(member))

        self.assertEqual(members, 3)
        self.assertEqual(vals, ['1', '2', '3'])

    def test_struct_mapped_prop_multi_list(self):
        overrides = [StructRPropGroup]
        _yaml = """
        - pgroup:
            - strprop: myval1.1
            - strprop: myval1.2
        - pgroup:
            strprop: myval2
        - pgroup:
            dictprop:
              p1: myval3
        """
        root = StructRSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        vals = []
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.pgroup), StructRPropGroup)
            self.assertEqual(len(leaf.pgroup), 3)
            for pgroup in leaf.pgroup:
                self.assertEqual(len(pgroup), 1)
                for member in pgroup:
                    self.assertTrue(type(member) in [StructRStrProp,
                                                     StructRDictProp])
                    for item in member:
                        if item._override_name == 'strprop':
                            self.assertEqual(type(item), StructRStrProp)
                            vals.append(item)
                        else:
                            self.assertEqual(type(item), StructRDictProp)
                            vals.append(item.p1)

        self.assertEqual(vals, ["myval1.1", "myval1.2", "myval2", "myval3"])

        # The following demonstrates using a shortcut that always returns the
        # last item added to the stack for any member. So basically is only
        # useful if there is only one item in any given member.
        vals = []
        for leaf in root.leaf_sections:
            for pgroup in leaf.pgroup:
                if pgroup.strprop:
                    self.assertEqual(type(pgroup.strprop), str)
                    vals.append(pgroup.strprop)
                else:
                    self.assertEqual(type(pgroup.dictprop), StructRDictProp)
                    vals.append(pgroup.dictprop.p1)

        self.assertEqual(vals, ["myval1.2", "myval2", "myval3"])

    def test_struct_mapped_prop_single_member_list(self):
        overrides = [StructRPropGroup]
        _yaml = """
        pgroup:
          - strprop: myval1
          - strprop: myval2
        """
        root = StructRSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        vals = []
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.pgroup), StructRPropGroup)
            # one because it is stacked
            self.assertEqual(len(leaf.pgroup), 1)
            for pgroup in leaf.pgroup:
                for member in pgroup:
                    self.assertEqual(type(member), StructRStrProp)
                    for item in member:
                        vals.append(item)

        self.assertEqual(vals, ["myval1", "myval2"])

    def test_struct_mapped_prop_single_member_list_nested(self):
        overrides = [StructRPropGroup]
        _yaml = """
        pgroup:
          - strprop: myval1
          - pgroup:
              strprop: myval2
        """
        root = StructRSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        vals = []
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.pgroup), StructRPropGroup)
            self.assertEqual(len(leaf.pgroup), 1)
            for pgroup in leaf.pgroup:
                for member in pgroup:
                    if member._override_name == 'pgroup':
                        # nested pgroup
                        self.assertEqual(type(member), StructRPropGroup)
                        self.assertEqual(len(member), 1)
                        for _pgroup in member:
                            for _member in _pgroup:
                                for _item in _member:
                                    vals.append(_item)
                    else:
                        self.assertEqual(type(member), StructRStrProp)
                        for item in member:
                            vals.append(item)

        self.assertEqual(vals, ["myval1", "myval2"])
