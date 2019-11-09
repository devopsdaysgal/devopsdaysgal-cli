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

import configargparse


class AutoEnvArgParser(configargparse.ArgumentParser):
    def add(self, *args, **kwargs):
        skip_env_var = kwargs.pop("skip_env_var", None)
        # allow for explict override
        if skip_env_var is not True and "env_var" not in kwargs:
            # find the long option
            longopt = [arg for arg in args if arg.startswith("--")][0]
            if longopt and longopt != "--help":
                envopt = longopt.lstrip("-").upper().replace("-", "_")
                kwargs["env_var"] = f"DODGCLI_{envopt}"

        return super().add(*args, **kwargs)
