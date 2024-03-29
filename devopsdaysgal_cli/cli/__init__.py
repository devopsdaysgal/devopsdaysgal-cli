#
# (c) Copyright 2019 Darragh Bailey
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#


import abc

import configargparse


class DodgCommand(abc.ABC):
    def __init__(self, parser: configargparse.ArgumentParser):
        self.parser = parser.add_parser(self.name)

    @abc.abstractmethod
    def add_args(self):
        pass

    def validate(self, options):
        return True

    @abc.abstractmethod
    def run(self, options):
        pass
