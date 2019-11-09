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

import logging
import traceback

import configargparse
from stevedore import extension

from devopsdaysgal_cli import parsers


class DevopsdaysGalCli(object):

    default_config_files = ["~/.devopsdaysgal-cli/config.yaml"]

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self):
        parser = parsers.AutoEnvArgParser(
            default_config_files=self.default_config_files,
            config_file_parser_class=configargparse.YAMLConfigFileParser,
            add_help=False,
        )

        # top level options
        parser.add("-c", "--config", is_config_file=True, help="config file path")
        parser.add(
            "-n",
            "--dry-run",
            action="store_true",
            default=False,
            help="Print out what would have been done.",
        )
        parser.add(
            "-h", "--help", action="store_true", default=False, help="Print help"
        )

        commandparser = parser.add_subparsers(
            dest="command", help="Conference management command to execute",
        )

        self.extension_manager = extension.ExtensionManager(
            namespace="devopsdaysgal.cli.subcommands",
            invoke_on_load=True,
            invoke_args=(commandparser,),
            on_load_failure_callback=self._report_subcommand_load_failure,
        )
        self.cmd_manager = {}

        def add_subcommand(ext):
            self.cmd_manager[ext.obj.name] = ext.obj
            ext.obj.add_args()

        self.extension_manager.map(add_subcommand)

        return parser

    @classmethod
    def _report_subcommand_load_failure(cls, mgr, ep, exc):
        raise RuntimeError(
            "There was a problem loading the subcommand defined by: '%s'.\n"
            "%s" % (ep, traceback.format_exc())
        )

    def run(self, args):

        logging.basicConfig(level=logging.INFO)

        options = self.parser.parse_args(args)
        if options.command:
            self.cmd_manager[options.command].run(options)
        elif options.help:
            self.parser.print_help()
        else:
            self.parser.error("must provide subcommand or --help")


def main(argv=None):

    if argv is None:
        import sys

        argv = sys.argv[1:]

    cli = DevopsdaysGalCli()
    cli.run(argv)


if __name__ == "__main__":
    main()
