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
from unittest import mock

from . import utils

from ystruct.ystruct import (
    YStructOverrideBase,
    YStructMappedOverrideBase,
    YStructSection,
)


class YStructCustomOverrideBase(YStructOverrideBase):
    pass


class YStructInput(YStructCustomOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['input']


class YStructMessage(YStructOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['message', 'message-alt']

    def __str__(self):
        return self.content


class YStructMeta(YStructOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['meta']


class YStructSettings(YStructOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['settings']

    @property
    def a_property(self):
        return "i am a property"


class YStructAction(YStructOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['action', 'altaction']


class YStructRaws(YStructOverrideBase):

    @classmethod
    def _override_keys(cls):
        return ['raws']


class YStructMappedGroupBase(YStructMappedOverrideBase):

    @classmethod
    def _override_mapped_member_types(cls):
        return [YStructSettings, YStructAction]

    @property
    def all(self):
        _all = {}
        if self.settings:
            _all['settings'] = self.settings.content

        if self.action:
            _all['action'] = self.action.content

        return _all


class YStructMappedGroupLogicalOpt(YStructMappedGroupBase):

    @classmethod
    def _override_keys(cls):
        return ['and', 'or', 'not']


class YStructMappedGroup(YStructMappedGroupBase):

    @classmethod
    def _override_keys(cls):
        return ['group']

    @classmethod
    def _override_mapped_member_types(cls):
        return super()._override_mapped_member_types() + \
                    [YStructMappedGroupLogicalOpt]


class YStructMappedRefsBase(YStructMappedOverrideBase):

    @classmethod
    def _override_mapped_member_types(cls):
        # has no members
        return []


class YStructMappedRefsLogicalOpt(YStructMappedRefsBase):

    @classmethod
    def _override_keys(cls):
        return ['and', 'or', 'not']


class YStructMappedRefs(YStructMappedRefsBase):

    @classmethod
    def _override_keys(cls):
        return ['refs']

    @classmethod
    def _override_mapped_member_types(cls):
        return super()._override_mapped_member_types() + \
                    [YStructMappedRefsLogicalOpt]


class TestYStruct(utils.BaseTestCase):

    def test_struct(self):
        overrides = [YStructInput, YStructMessage, YStructSettings,
                     YStructMeta]
        with open('examples/checks.yaml') as fd:
            root = YStructSection('fruit tastiness', yaml.safe_load(fd.read()),
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
        overrides = [YStructInput, YStructMessage, YStructSettings]
        root = YStructSection('root', content={}, override_handlers=overrides)
        for leaf in root.leaf_sections:
            self.assertEqual(leaf.input.type, 'dict')

    def test_struct_w_mapping(self):
        with open('examples/checks2.yaml') as fd:
            root = YStructSection('atest', yaml.safe_load(fd.read()),
                                  override_handlers=[YStructMessage,
                                                     YStructMappedGroup])
            for leaf in root.leaf_sections:
                self.assertTrue(leaf.name in ['item1', 'item2', 'item3',
                                              'item4', 'item5'])
                if leaf.name == 'item1':
                    self.assertEqual(leaf.group.settings.plum, 'pie')
                    self.assertEqual(leaf.group.action.eat, 'now')
                    self.assertEqual(leaf.group.all,
                                     {'settings': {'plum': 'pie'},
                                      'action': {'eat': 'now'}})
                elif leaf.name == 'item2':
                    self.assertEqual(leaf.group.settings.apple, 'tart')
                    self.assertEqual(leaf.group.action.eat, 'later')
                    self.assertEqual(leaf.group.all,
                                     {'settings': {'apple': 'tart'},
                                      'action': {'eat': 'later'}})
                elif leaf.name == 'item3':
                    self.assertEqual(str(leaf.message), 'message not mapped')
                    self.assertEqual(leaf.group.settings.ice, 'cream')
                    self.assertEqual(leaf.group.action, None)
                    self.assertEqual(leaf.group.all,
                                     {'settings': {'ice': 'cream'}})
                elif leaf.name == 'item4':
                    self.assertEqual(leaf.group.settings.treacle, 'tart')
                    self.assertEqual(leaf.group.action.want, 'more')
                    self.assertEqual(leaf.group.all,
                                     {'settings': {'treacle': 'tart'},
                                      'action': {'want': 'more'}})
                elif leaf.name == 'item5':
                    self.assertEqual(len(leaf.group), 3)
                    checked = 0
                    for i, _group in enumerate(leaf.group):
                        if i == 0:
                            checked += 1
                            self.assertEqual(_group.settings.strawberry,
                                             'jam')
                            self.assertEqual(_group.action.lots, 'please')
                        elif i == 1:
                            checked += 1
                            self.assertEqual(_group.settings.cherry, 'jam')
                            self.assertEqual(_group.action.lots, 'more')
                        elif i == 2:
                            checked += 1
                            self.assertEqual(_group.settings.cherry, 'jam')
                            self.assertEqual(_group.action.lots, 'more')
                            self.assertEqual(_group.altaction.still, 'more')

                    self.assertEqual(checked, 3)

    def test_struct_w_metagroup_list(self):
        s1 = {'settings': {'result': True}}
        s2 = {'settings': {'result': False}}

        content = {'item1': {'group': [s1, s2]}}

        root = YStructSection('mgtest', content,
                              override_handlers=[YStructMappedGroup])
        for leaf in root.leaf_sections:
            self.assertEqual(len(leaf.group), 1)
            self.assertEqual(len(leaf.group.settings), 2)
            results = [s.result for s in leaf.group.settings]

        self.assertEqual(results, [True, False])

    def test_struct_w_metagroup_w_logical_opt(self):
        s1 = {'settings': {'result': True}}
        s2 = {'settings': {'result': False}}

        content = {'item1': {'group': {'and': [s1, s2]}}}

        root = YStructSection('mgtest', content,
                              override_handlers=[YStructMappedGroup])
        for leaf in root.leaf_sections:
            self.assertEqual(len(leaf.group), 1)
            self.assertEqual(len(getattr(leaf.group, 'and').settings), 2)
            results = [s.result for s in getattr(leaf.group, 'and').settings]

        self.assertEqual(results, [True, False])

    def test_struct_w_metagroup_w_multiple_logical_opts(self):
        s1 = {'settings': {'result': True}}
        s2 = {'settings': {'result': False}}
        s3 = {'settings': {'result': False}}

        content = {'item1': {'group': {'or': [s1, s2],
                                       'and': s3}}}

        root = YStructSection('mgtest', content,
                              override_handlers=[YStructMappedGroup])
        for leaf in root.leaf_sections:
            self.assertEqual(len(leaf.group), 1)
            self.assertEqual(len(getattr(leaf.group, 'and').settings), 1)
            self.assertEqual(len(getattr(leaf.group, 'or').settings), 2)
            results = [s.result for s in getattr(leaf.group, 'and').settings]
            self.assertEqual(results, [False])
            results = [s.result for s in getattr(leaf.group, 'or').settings]

        self.assertEqual(results, [True, False])

    def test_struct_w_metagroup_w_mixed_list(self):
        s1 = {'settings': {'result': True}}
        s2 = {'settings': {'result': False}}

        content = {'item1': {'group': [{'or': s1}, s2]}}

        root = YStructSection('mgtest', content,
                              override_handlers=[YStructMappedGroup])
        for leaf in root.leaf_sections:
            self.assertEqual(len(leaf.group), 1)
            self.assertEqual(len(getattr(leaf.group, 'or').settings), 1)
            self.assertEqual(len(getattr(leaf.group, 'or')), 1)
            results = []
            for groupitem in leaf.group:
                for item in groupitem:
                    if item._override_name == 'or':
                        for settings in item:
                            for entry in settings:
                                results.append(entry.result)
                    else:
                        for settings in item:
                            results.append(settings.result)

        self.assertEqual(sorted(results), sorted([True, False]))

    def test_struct_w_metagroup_w_mixed_list_w_str_overrides(self):
        content = {'item1': {'refs': [{'or': 'ref1',
                                       'and': ['ref2', 'ref3']}, 'ref4']}}

        root = YStructSection('mgtest', content,
                              override_handlers=[YStructMappedRefs])
        results = []
        for leaf in root.leaf_sections:
            self.assertEqual(leaf.name, 'item1')
            for refs in leaf.refs:
                self.assertEqual(refs.name, 'refs')
                for item in refs:
                    self.assertTrue(item._override_name in ['and', 'or',
                                                            'ref4'])
                    if item._override_name == 'or':
                        self.assertEqual(len(item), 1)
                        for subitem in item.members:
                            results.append(subitem._override_name)
                    elif item._override_name == 'and':
                        self.assertEqual(len(item), 1)
                        for subitem in item.members:
                            results.append(subitem._override_name)
                    else:
                        results.append(item._override_name)

        self.assertEqual(sorted(results),
                         sorted(['ref1', 'ref2', 'ref3', 'ref4']))

    @mock.patch.object(YStructSection, 'post_hook')
    @mock.patch.object(YStructSection, 'pre_hook')
    def test_hooks_called(self, mock_pre_hook, mock_post_hook):
        content = {'myroot': {
                       'leaf1': {'settings': {'brake': 'off'}},
                       'leaf2': {'settings': {'clutch': 'on'}}}}

        YStructSection('hooktest', content,
                       override_handlers=[YStructMappedGroup],
                       run_hooks=False)
        self.assertFalse(mock_pre_hook.called)
        self.assertFalse(mock_post_hook.called)

        YStructSection('hooktest', content,
                       override_handlers=[YStructMappedGroup],
                       run_hooks=True)
        self.assertTrue(mock_pre_hook.called)
        self.assertTrue(mock_post_hook.called)

    def test_resolve_paths(self):
        content = {'myroot': {
                       'sub1': {
                           'sub2': {
                               'leaf1': {'settings': {'brake': 'off'},
                                         'action': 'go'},
                               'leaf2': {'settings': {'clutch': 'on'}}}},
                       'sub3': {
                               'leaf3': {'settings': {'brake': 'off'}}}}}

        root = YStructSection('resolvtest', content,
                              override_handlers=[YStructMappedGroup])
        resolved = []
        for leaf in root.leaf_sections:
            resolved.append(leaf.resolve_path)
            resolved.append(leaf.group._override_path)
            for setting in leaf.group.members:
                resolved.append(setting._override_path)

        expected = ['resolvtest.myroot.sub1.sub2.leaf1',
                    'resolvtest.myroot.sub1.sub2.leaf2',
                    'resolvtest.myroot.sub3.leaf3',
                    'resolvtest.myroot.sub1.sub2.leaf1.group.action',
                    'resolvtest.myroot.sub1.sub2.leaf1.group.settings',
                    'resolvtest.myroot.sub1.sub2.leaf1.group',
                    'resolvtest.myroot.sub1.sub2.leaf2.group',
                    'resolvtest.myroot.sub1.sub2.leaf2.group.settings',
                    'resolvtest.myroot.sub3.leaf3.group',
                    'resolvtest.myroot.sub3.leaf3.group.settings']

        self.assertEqual(sorted(resolved),
                         sorted(expected))

    def test_context(self):
        content = {'myroot': {'leaf1': {'settings': {'brake': 'off'}}}}

        class ContextHandler(object):
            def __init__(self):
                self.context = {}

            def set(self, key, value):
                self.context[key] = value

            def get(self, key):
                return self.context.get(key)

        root = YStructSection('contexttest', content,
                              override_handlers=[YStructMappedGroup],
                              context=ContextHandler())
        for leaf in root.leaf_sections:
            for setting in leaf.group.members:
                self.assertIsNone(setting.context.get('k1'))
                setting.context.set('k1', 'notk2')
                self.assertEqual(setting.context.get('k1'), 'notk2')

    def test_raw_types(self):
        content = {'raws': {'red': 'meat',
                            'bits': 8,
                            'bytes': 1,
                            'stringbits': '8'}}
        root = YStructSection('rawtest', content,
                              override_handlers=[YStructRaws])
        for leaf in root.leaf_sections:
            self.assertEqual(leaf.raws.red, 'meat')
            self.assertEqual(leaf.raws.bytes, 1)
            self.assertEqual(leaf.raws.bits, 8)
            self.assertEqual(leaf.raws.stringbits, '8')
