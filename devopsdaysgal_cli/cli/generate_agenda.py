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
from trello import TrelloClient

from devopsdaysgal_cli import cli


class Command(cli.DodgCommand):
    """
    Output agenda generated from tasks status in Trello
    """

    name = "generate-agenda"

    default_board_name = "Devopsdays Galway 2019"
    default_board_list = "Doing"

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
        self.parser.add_argument(
            "-h",
            "--help",
            action="store_true",
            default=False,
            help="Print help for this command",
        )

    def run(self, options):
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
                inprogess_list = list
                break
        else:
            self.parser.error(
                f"Failed to locate list '{self.default_board_list}' to build agenda"
            )

        board_members = {
            member.id: member.full_name for member in conference_board.get_members()
        }

        # TODO: look at generating user specific lists to ping each user
        agenda = []
        for card in inprogess_list.list_cards():
            if not card.idMembers:
                agenda.append(f"<to-be-assigned>: {card.name}")
                continue

            assignees = ", ".join([board_members[id] for id in card.idMembers])
            agenda.append(f"{assignees}: {card.name}")

        print("\n".join(sorted(agenda)))
