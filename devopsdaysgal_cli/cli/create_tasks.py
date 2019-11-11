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

import platform
import sys

from trello import TrelloClient

from devopsdaysgal_cli import cli


class Command(cli.DodgCommand):
    """
    Output agenda generated from tasks status in Trello
    """

    name = "generate-agenda"

    default_board_name = "Devopsdays Galway 2019"
    default_board_list = "Ready to Pick Up"

    def add_args(self):
        self.parser.add(
            "-t",
            "--trello-key",
            action="store",
            required=True,
            help="Trello key to go with secret token for access",
        )
        self.parser.add(
            "-s",
            "--trello-secret",
            action="store",
            required=True,
            help="Trello secret token for auth",
        )
        self.parser.add(
            "-b",
            "--trello-board",
            action="store",
            help="Board name to perform operations on.",
            default=self.default_board_name,
        )
        self.parser.add(
            "-a",
            "--agenda",
            action="store",
            help="Agenda text to convert to cards in Trello.",
            default=sys.stdin,
        )
        self.parser.add_argument(
            "-h",
            "--help",
            action="store_true",
            default=False,
            help="Print help for this command",
        )

    def run(self, options):
        if hasattr(options.agenda, "read"):
            self.logger.debug("Input text is via stdin")
            if options.agenda.isatty():
                if platform.system() == "Windows":
                    key = "CTRL+Z"
                else:
                    key = "CTRL+D"
                self.logger.warning(f"Reading agenda text from STDIN. Press {key} to end input")

            tasklist = options.agenda.read()
        else:
            tasklist = options.agenda

        client = TrelloClient(
            api_key=options.trello_key, api_secret=options.trello_secret,
        )

        for board in client.list_boards():
            if board.name == options.trello_board:
                conference_board = board
                break
        else:
            self.parser.error(f"Failed to locate board: {options.trello_board}")

        for list in conference_board.list_lists():
            if list.name == self.default_board_list:
                ready_list = list
                break
        else:
            self.parser.error(
                f"Failed to locate list '{self.default_board_list}' to add tasks to from agenda"
            )

        board_members = {
            member.id: member.full_name for member in conference_board.get_members()
        }
        board_members_by_name = {
            name: id for id, name in board_members.items()
        }

        for task in tasklist.split("\n"):
            assignee, task_name = task.partition(":", 1)
            # first check to see if we need to add the task
            existing_cards = client.search(
                query=task_name, partial_match=True, models=["cards"], board_ids=[conference_board.id]
            )

            if existing_cards:
                print("Is this covered by one of the following cards:")
                for card in existing_cards:
                    print(card.name)

            if assignee not in board_members_by_name:
                # need to ask who will assigned this
                pass