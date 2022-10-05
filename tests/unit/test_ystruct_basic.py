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

from ystruct.ystruct import (
    YStructOverrideBase,
    YStructMappedOverrideBase,
    YStructSection,
)


class YStructStrProp(YStructOverrideBase, UserString):

    @classmethod
    def _override_keys(cls):
        return ['strprop']

    @property
    def data(self):
        return self.content


class YStructDictProp(YStructOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['dictprop']


class YStructPropGroup(YStructMappedOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['pgroup']

    @classmethod
    def _override_mapped_member_types(cls):
        return [YStructStrProp, YStructDictProp]


class TestYStructSimpleProps(utils.BaseTestCase):

    def test_struct_simple_prop_single(self):
        overrides = [YStructStrProp]
        _yaml = """
        strprop: myval
        """
        root = YStructSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.strprop), YStructStrProp)
            self.assertEqual(leaf.strprop, "myval")

    def test_struct_simple_prop_multi(self):
        overrides = [YStructStrProp]
        _yaml = """
        s1:
          strprop: myval1
        s2:
          strprop: myval2
        """
        root = YStructSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.strprop), YStructStrProp)
            if leaf.name == 's1':
                self.assertEqual(leaf.strprop, "myval1")
            else:
                self.assertEqual(leaf.strprop, "myval2")

    def test_struct_simple_prop_single_list(self):
        overrides = [YStructStrProp]
        _yaml = """
        - strprop: myval1
        - strprop: myval2
        """
        root = YStructSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        vals = []
        for leaf in root.leaf_sections:
            for prop in leaf.strprop:
                self.assertEqual(type(prop), YStructStrProp)
                vals.append(prop)

            self.assertEqual(vals, ["myval1", "myval2"])


class TestYStructMappedProps(utils.BaseTestCase):

    def test_struct_mapped_prop_single(self):
        overrides = [YStructPropGroup]
        _yaml = """
        pgroup:
          strprop: myval
        """
        root = YStructSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.pgroup), YStructPropGroup)
            self.assertEqual(len(leaf.pgroup), 1)
            for member in leaf.pgroup:
                self.assertEqual(type(member.strprop), str)
                self.assertEqual(member.strprop, "myval")

    def test_struct_mapped_prop_multi_list(self):
        overrides = [YStructPropGroup]
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
        root = YStructSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        vals = []
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.pgroup), YStructPropGroup)
            self.assertEqual(len(leaf.pgroup), 3)
            for pgroup in leaf.pgroup:
                self.assertEqual(len(pgroup), 1)
                for member in pgroup:
                    self.assertTrue(type(member) in [YStructStrProp,
                                                     YStructDictProp])
                    for item in member:
                        if item._override_name == 'strprop':
                            self.assertEqual(type(item), YStructStrProp)
                            vals.append(item)
                        else:
                            self.assertEqual(type(item), YStructDictProp)
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
                    self.assertEqual(type(pgroup.dictprop), YStructDictProp)
                    vals.append(pgroup.dictprop.p1)

        self.assertEqual(vals, ["myval1.2", "myval2", "myval3"])

    def test_struct_mapped_prop_single_member_list(self):
        overrides = [YStructPropGroup]
        _yaml = """
        pgroup:
          - strprop: myval1
          - strprop: myval2
        """
        root = YStructSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        vals = []
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.pgroup), YStructPropGroup)
            # one because it is stacked
            self.assertEqual(len(leaf.pgroup), 1)
            for pgroup in leaf.pgroup:
                for member in pgroup:
                    self.assertEqual(type(member), YStructStrProp)
                    for item in member:
                        vals.append(item)

        self.assertEqual(vals, ["myval1", "myval2"])

    def test_struct_mapped_prop_single_member_list_nested(self):
        overrides = [YStructPropGroup]
        _yaml = """
        pgroup:
          - strprop: myval1
          - pgroup:
              strprop: myval2
        """
        root = YStructSection('simpletest', yaml.safe_load(_yaml),
                              override_handlers=overrides)
        vals = []
        for leaf in root.leaf_sections:
            self.assertEqual(type(leaf.pgroup), YStructPropGroup)
            self.assertEqual(len(leaf.pgroup), 1)
            for pgroup in leaf.pgroup:
                for member in pgroup:
                    if member._override_name == 'pgroup':
                        # nested pgroup
                        self.assertEqual(type(member), YStructPropGroup)
                        self.assertEqual(len(member), 1)
                        for _pgroup in member:
                            for _member in _pgroup:
                                for _item in _member:
                                    vals.append(_item)
                    else:
                        self.assertEqual(type(member), YStructStrProp)
                        for item in member:
                            vals.append(item)

        self.assertEqual(vals, ["myval1", "myval2"])
