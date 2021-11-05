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


class YStructException(Exception):
    pass


class YAMLDefOverrideBase(object):
    KEY = None

    def __init__(self, content):
        self._content = content

    @property
    def content(self):
        return self._content

    def __dict__(self, name):
        name = name.replace('-', '_')
        return self.content[name]

    def __getattr__(self, name):
        name = name.replace('-', '_')
        return self.content.get(name)


class YAMLDefBase(object):
    # We want these to be global/common to all sections
    _override_handlers = []

    def _find_leaf_sections(self, section):
        if section.is_leaf:
            return [section]

        leaves = []
        for s in section.sections:
            leaves += self._find_leaf_sections(s)

        return leaves

    @property
    def branch_sections(self):
        return [s.parent for s in self.leaf_sections]

    @property
    def leaf_sections(self):
        return self._find_leaf_sections(self)

    @property
    def override_keys(self):
        return [o.KEY for o in self._override_handlers]

    def get_override_handler(self, name):
        for o in self._override_handlers:
            if o.KEY == name:
                return o

    def set_override_handlers(self, override_handlers):
        self._override_handlers += override_handlers


class YAMLDefSection(YAMLDefBase):
    def __init__(self, name, content, overrides=None, parent=None,
                 override_handlers=None):
        self.name = name
        self.parent = parent
        self.content = content
        self.sections = []
        self.overrides = overrides or {}
        if override_handlers:
            self.set_override_handlers(override_handlers)

        self.run()

    def run(self):
        if type(self.content) != dict:
            raise YStructException("undefined override '{}'".format(self.name))

        for name, content in self.content.items():
            if name in self.override_keys:
                handler = self.get_override_handler(name)
                self.overrides[name] = handler(content)
                continue

            s = YAMLDefSection(name, content, self.overrides, parent=self)
            self.sections.append(s)

    @property
    def is_leaf(self):
        return len(self.sections) == 0

    def __dict__(self, name):
        name = name.replace('-', '_')
        return self.overrides[name]

    def __getattr__(self, name):
        name = name.replace('-', '_')
        return self.overrides.get(name)
