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

import datetime
import json
import os

import requests
import requests.auth

from devopsdaysgal_cli import cli


class Command(cli.DodgCommand):
    """
    Create some tickets using RSVP lists to be shared using the url
    """

    name = "make-tickets"

    def add_args(self):
        self.parser.add(
            "-s",
            "--tito-secret",
            action="store",
            required=True,
            help="Ti.to API secret token for auth",
        )
        self.parser.add(
            "-t",
            "--tito-account",
            action="store",
            help="Event name to perform operations on.",
            default="devopsdays-galway",
        )
        self.parser.add(
            "-e",
            "--tito-event",
            action="store",
            help="Event name to perform operations on.",
            default=str(datetime.datetime.now().year),
        )
        self.parser.add(
            "-a",
            "--anonymous",
            action="store_true",
            help="Whether to generate tickets for sharing to unknown recipients",
            default=False,
        )
        self.parser.add(
            "-n",
            "--name",
            action="store",
            required=True,
            help="List name to group the created tickets under",
        )
        self.parser.add(
            "-T",
            "--ticket",
            action="store",
            required=True,
            help="Ticket Type to use for RSVP invitations",
        )
        self.parser.add(
            "-c",
            "--count",
            type=int,
            help="Number of tickets that should exist",
            default=2,
        )
        self.parser.add_argument(
            "-h",
            "--help",
            action="store_true",
            default=False,
            help="Print help for this command",
        )

    def _get(self, endpoint, params=None):

        url = f"{self.api_url}/{endpoint}"
        resp = self.session.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            return data.get(os.path.basename(endpoint), {})

        return {}

    def _post(self, endpoint, payload=None):

        url = f"{self.api_url}/{endpoint}"
        resp = self.session.post(url, json=payload)

        resp.raise_for_status()

        data = resp.json()
        return data

    def run(self, options):
        self.api_url = f"https://api.tito.io/v3/{options.tito_account}/{options.tito_event}"
        self.session = requests.Session()
        self.session.headers['Authorization'] = f"Token token={options.tito_secret}"
        self.session.headers['Accept'] = "application/json"
        self.session.headers['Content-Type'] = "application/json"

        if not options.anonymous:
            self.parser.error("Currently only support anonymous RSVP ticket creation")
            return 2

        # check if the specified list already exists
        rsvp_lists = {
            rsvp_list["title"]: rsvp_list for rsvp_list in self._get("rsvp_lists")
        }

        rsvp_list = rsvp_lists.get(options.name)
        if not rsvp_list:
            if options.dry_run:
                rsvp_list = {'slug': '<dry-run-not-created>'}
            else:
                rsvp_list = self._post("rsvp_lists", {"rsvp_list": {"title": options.name}})

        if options.dry_run:
            rsvp_invitations = []
        else:
            rsvp_invitations = self._get(f"rsvp_lists/{rsvp_list['slug']}/release_invitations")

        releases = {
            release["title"].lower(): release for release in self._get("releases")
        }
        release = releases.get(options.ticket.lower())
        if not release:
            self.parser.error(
                f"Unrecognized ticket type '{options.ticket}', please use one of the following:\n"
                + "\n".join(releases.keys())
            )
            return 1

        if options.anonymous:
            num_invitations = len(rsvp_invitations)
            if num_invitations >= options.count:
                print(f"{options.name} already has {num_invitations} invitations")
                for invitation in rsvp_invitations:
                    print(invitation["unique_url"])
                return 0

            print("Number of current invitations = %d" % len(rsvp_invitations))
            while num_invitations < options.count:
                params = {
                    "release_invitation": {
                        "email": "galway@devopsdays.org",
                        "release_ids": [release["id"]],
                        "redirect": True,
                    }
                }
                endpoint = f"rsvp_lists/{rsvp_list['slug']}/release_invitations"
                if options.dry_run:
                    print(f"Would have posted 1 request to '{self.api_url}/{endpoint}'")
                else:
                    invitation = self._post(f"rsvp_lists/{rsvp_list['slug']}/release_invitations", params)
                    print(invitation["release_invitation"]["unique_url"])
                num_invitations = num_invitations + 1

            return 0
