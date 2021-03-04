# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

import responses

from libtbdata import bugzilla, handler
from libtbdata.connection import Query
from tests.auto_mock import MockTestCase


class BugIDTest(MockTestCase):

    mock_urls = [bugzilla.Bugzilla.URL]

    @responses.activate
    def test_bugid(self):
        def bughandler(bug, data):
            data.update(bug)

        bug = {}
        bugzilla.Bugzilla(12345, bughandler=bughandler, bugdata=bug).get_data().wait()

        self.assertEqual(bug["id"], 12345)
        self.assertEqual(bug["resolution"], u"FIXED")
        self.assertEqual(bug["assigned_to"], u"jefft@formerly-netscape.com.tld")
        self.assertEqual(
            bug["summary"],
            u"[DOGFOOD] Unable to Forward a message received as an Inline page or an attachment",
        )

    @responses.activate
    def test_bugids(self):
        def bughandler(bug, data):
            data[bug["id"]] = bug

        bugs = {}
        bugzilla.Bugzilla(
            [12345, 12346], bughandler=bughandler, bugdata=bugs
        ).get_data().wait()

        self.assertEqual(bugs[12345]["id"], 12345)
        self.assertEqual(bugs[12345]["resolution"], u"FIXED")
        self.assertEqual(bugs[12345]["assigned_to"], u"jefft@formerly-netscape.com.tld")
        self.assertEqual(
            bugs[12345]["summary"],
            u"[DOGFOOD] Unable to Forward a message received as an Inline page or an attachment",
        )

        self.assertEqual(bugs[12346]["id"], 12346)
        self.assertEqual(bugs[12346]["resolution"], u"FIXED")
        self.assertEqual(bugs[12346]["assigned_to"], u"doug.turner@gmail.com")
        self.assertEqual(
            bugs[12346]["summary"], u"nsOutputFileStream should buffer the output"
        )

    @responses.activate
    def test_bugids_multihandlers1(self):
        def bughandler1(bug, data):
            data[bug["id"]] = bug

        def bughandler2(bug, data):
            data[bug["id"]] = bug

        bugs1 = {}
        bugs2 = {}
        h1 = handler.Handler(bughandler1, bugs1)
        h2 = handler.Handler(bughandler2, bugs2)
        bugzilla.Bugzilla(
            [12345, 12346], bughandler=handler.MultipleHandler(h1, h2)
        ).get_data().wait()

        for bugs in [bugs1, bugs2]:
            self.assertEqual(bugs[12345]["id"], 12345)
            self.assertEqual(bugs[12345]["resolution"], u"FIXED")
            self.assertEqual(
                bugs[12345]["assigned_to"], u"jefft@formerly-netscape.com.tld"
            )
            self.assertEqual(
                bugs[12345]["summary"],
                u"[DOGFOOD] Unable to Forward a message received as an Inline page or an attachment",
            )

            self.assertEqual(bugs[12346]["id"], 12346)
            self.assertEqual(bugs[12346]["resolution"], u"FIXED")
            self.assertEqual(bugs[12346]["assigned_to"], u"doug.turner@gmail.com")
            self.assertEqual(
                bugs[12346]["summary"], u"nsOutputFileStream should buffer the output"
            )

    @responses.activate
    def test_bugids_multihandlers2(self):
        bugs1 = {}
        bugs2 = {}
        bugs3 = {}

        def bughandler1(bug):
            bugs1[bug["id"]] = bug

        def bughandler2(bug):
            bugs2[bug["id"]] = bug

        def bughandler3(bug, data):
            data[bug["id"]] = bug

        bugzilla.Bugzilla(
            [12345, 12346], bughandler=[bughandler1, bughandler2, (bughandler3, bugs3)]
        ).get_data().wait()

        for bugs in [bugs1, bugs2, bugs3]:
            self.assertEqual(bugs[12345]["id"], 12345)
            self.assertEqual(bugs[12345]["resolution"], u"FIXED")
            self.assertEqual(
                bugs[12345]["assigned_to"], u"jefft@formerly-netscape.com.tld"
            )
            self.assertEqual(
                bugs[12345]["summary"],
                u"[DOGFOOD] Unable to Forward a message received as an Inline page or an attachment",
            )

            self.assertEqual(bugs[12346]["id"], 12346)
            self.assertEqual(bugs[12346]["resolution"], u"FIXED")
            self.assertEqual(bugs[12346]["assigned_to"], u"doug.turner@gmail.com")
            self.assertEqual(
                bugs[12346]["summary"], u"nsOutputFileStream should buffer the output"
            )

    @responses.activate
    def test_merge(self):
        def bughandler1(bug, data):
            data[bug["id"]] = bug

        def bughandler2(bug, data):
            data[bug["id"]] = bug

        bugs1 = {}
        bugs2 = {}
        bz1 = bugzilla.Bugzilla(
            [12345, 12346], include_fields=["id"], bughandler=bughandler1, bugdata=bugs1
        )
        bz2 = bugzilla.Bugzilla(
            [12345, 12346],
            include_fields=["id", "resolution"],
            bughandler=bughandler2,
            bugdata=bugs2,
        )

        bz1.merge(bz2).get_data().wait()

        self.assertEqual(bugs1[12345]["id"], 12345)
        self.assertEqual(bugs1[12346]["id"], 12346)
        self.assertEqual(bugs2[12345]["id"], 12345)
        self.assertEqual(bugs2[12345]["resolution"], u"FIXED")
        self.assertEqual(bugs2[12346]["id"], 12346)
        self.assertEqual(bugs2[12346]["resolution"], u"FIXED")

    @responses.activate
    def test_queries(self):
        bugs = {}

        def bughandler(data):
            bug = data["bugs"][0]
            bugs[bug["id"]] = bug

        queries = [
            Query(bugzilla.Bugzilla.API_URL, {"id": "12345"}, bughandler),
            Query(bugzilla.Bugzilla.API_URL, {"id": "12346"}, bughandler),
        ]

        bugzilla.Bugzilla(queries=queries, bughandler=bughandler).wait()

        self.assertEqual(bugs[12345]["id"], 12345)
        self.assertEqual(bugs[12345]["resolution"], u"FIXED")
        self.assertEqual(bugs[12345]["assigned_to"], u"jefft@formerly-netscape.com.tld")
        self.assertEqual(
            bugs[12345]["summary"],
            u"[DOGFOOD] Unable to Forward a message received as an Inline page or an attachment",
        )

        self.assertEqual(bugs[12346]["id"], 12346)
        self.assertEqual(bugs[12346]["resolution"], u"FIXED")
        self.assertEqual(bugs[12346]["assigned_to"], u"doug.turner@gmail.com")
        self.assertEqual(
            bugs[12346]["summary"], u"nsOutputFileStream should buffer the output"
        )

    @responses.activate
    def test_empty_queries(self):
        bugs = {}

        def bughandler(data):
            bug = data["bugs"][0]
            bugs[bug["id"]] = bug

        bugzilla.Bugzilla(queries=[], bughandler=bughandler).wait()

        self.assertEqual(bugs, {})

    @responses.activate
    def test_search(self):
        def bughandler(bug, data):
            data[bug["id"]] = bug

        bugs = {}

        bugzilla.Bugzilla(
            "bug_id=12345%2C12346&bug_id_type=anyexact&list_id=12958345&resolution=FIXED&query_format=advanced",
            bughandler=bughandler,
            bugdata=bugs,
        ).get_data().wait()

        self.assertEqual(bugs[12345]["id"], 12345)
        self.assertEqual(bugs[12346]["id"], 12346)

    @responses.activate
    def test_search_dict(self):
        def bughandler(bug, data):
            data[bug["id"]] = bug

        bugs = {}

        # Unique bug id
        terms = {
            "bug_id": 12345,
            "bug_id_type": "anyexact",
            "list_id": 12958345,
            "resolution": "FIXED",
            "query_format": "advanced",
        }
        bugzilla.Bugzilla(terms, bughandler=bughandler, bugdata=bugs).get_data().wait()

        self.assertEqual(len(bugs), 1)
        self.assertEqual(bugs[12345]["id"], 12345)

        bugs = {}

        # Multiple bugs
        terms = {
            "bug_id": [12345, 12346],
            "bug_id_type": "anyexact",
            "list_id": 12958345,
            "resolution": "FIXED",
            "query_format": "advanced",
        }
        bugzilla.Bugzilla(terms, bughandler=bughandler, bugdata=bugs).get_data().wait()

        self.assertEqual(len(bugs), 2)
        self.assertEqual(bugs[12345]["id"], 12345)
        self.assertEqual(bugs[12346]["id"], 12346)

        bugs = {}

        # Multiple queries
        terms = [{"bug_id": 12345}, {"bug_id": 12346}]
        bugzilla.Bugzilla(terms, bughandler=bughandler, bugdata=bugs).get_data().wait()

        self.assertEqual(len(bugs), 2)
        self.assertEqual(bugs[12345]["id"], 12345)
        self.assertEqual(bugs[12346]["id"], 12346)

    @responses.activate
    def test_search_multiple(self):
        def bughandler(bug, data):
            data[bug["id"]] = bug

        bugs = {}
        bugzilla.Bugzilla(
            ["bug_id=12345%2C12346%2C12347", "bug_id=12348%2C12349%2C12350"],
            bughandler=bughandler,
            bugdata=bugs,
        ).get_data().wait()

        self.assertEqual(bugs[12345]["id"], 12345)
        self.assertEqual(bugs[12346]["id"], 12346)
        self.assertEqual(bugs[12347]["id"], 12347)
        self.assertEqual(bugs[12348]["id"], 12348)
        self.assertEqual(bugs[12349]["id"], 12349)
        self.assertEqual(bugs[12350]["id"], 12350)


class BugCommentHistoryTest(MockTestCase):

    mock_urls = [bugzilla.Bugzilla.URL]

    @responses.activate
    def test_bugid(self):
        def bughandler(bug, data):
            data["bug"] = bug

        def commenthandler(bug, bugid, data):
            data["comment"] = bug["comments"]

        def historyhandler(bug, data):
            data["history"] = bug

        data = {}
        bugzilla.Bugzilla(
            12345,
            bughandler=bughandler,
            bugdata=data,
            commenthandler=commenthandler,
            commentdata=data,
            historyhandler=historyhandler,
            historydata=data,
        ).get_data().wait()

        self.assertEqual(data["bug"]["id"], 12345)
        self.assertEqual(len(data["comment"]), 19)
        self.assertTrue(data["comment"][0]["text"].startswith(u"Steps to reproduce"))
        self.assertEqual(len(data["history"]["history"]), 24)

    @responses.activate
    def test_search(self):
        def bughandler(bug, data):
            data["bug"] = bug

        def commenthandler(bug, bugid, data):
            data["comment"] = bug["comments"]

        def historyhandler(bug, data):
            data["history"] = bug

        data = {}
        bugzilla.Bugzilla(
            "bug_id=12345",
            bughandler=bughandler,
            bugdata=data,
            commenthandler=commenthandler,
            commentdata=data,
            historyhandler=historyhandler,
            historydata=data,
        ).get_data().wait()

        self.assertEqual(data["bug"]["id"], 12345)
        self.assertEqual(len(data["comment"]), 19)
        self.assertTrue(data["comment"][0]["text"].startswith(u"Steps to reproduce"))
        self.assertEqual(len(data["history"]["history"]), 24)

    @responses.activate
    def test_search_history(self):
        def historyhandler(bug, data):
            data["history"] = bug["history"]

        data = {}
        bugzilla.Bugzilla(
            12345, historyhandler=historyhandler, historydata=data
        ).get_data().wait()

        all = bugzilla.Bugzilla.get_history_matches(data["history"], {})
        self.assertEqual(len(all), len(data["history"]))

        change_to_assigned = bugzilla.Bugzilla.get_history_matches(
            data["history"], {"added": "ASSIGNED"}
        )
        self.assertEqual(
            change_to_assigned,
            [
                {
                    "when": "1999-08-29T17:43:15Z",
                    "changes": [
                        {"added": "ASSIGNED", "field_name": "status", "removed": "NEW"}
                    ],
                    "who": "jefft@formerly-netscape.com.tld",
                }
            ],
        )

        blocks_changes = bugzilla.Bugzilla.get_history_matches(
            data["history"], {"field_name": "blocks"}
        )
        self.assertEqual(
            blocks_changes,
            [
                {
                    "changes": [
                        {"removed": "", "added": "11091", "field_name": "blocks"}
                    ],
                    "who": "lchiang@formerly-netscape.com.tld",
                    "when": "1999-09-20T22:58:39Z",
                },
                {
                    "changes": [
                        {"removed": "", "added": "17976", "field_name": "blocks"}
                    ],
                    "who": "chofmann@gmail.com",
                    "when": "1999-11-04T14:05:18Z",
                },
            ],
        )

        single_block_change = bugzilla.Bugzilla.get_history_matches(
            data["history"], {"added": "11091", "field_name": "blocks"}
        )
        self.assertEqual(
            single_block_change,
            [
                {
                    "changes": [
                        {"removed": "", "added": "11091", "field_name": "blocks"}
                    ],
                    "who": "lchiang@formerly-netscape.com.tld",
                    "when": "1999-09-20T22:58:39Z",
                }
            ],
        )

        data = {}
        bugzilla.Bugzilla(
            1005958, historyhandler=historyhandler, historydata=data
        ).get_data().wait()

        multiple_changes = bugzilla.Bugzilla.get_history_matches(
            data["history"], {"added": "approval-mozilla-release?"}
        )
        self.assertEqual(
            multiple_changes,
            [
                {
                    "changes": [
                        {
                            "added": "approval-mozilla-aurora?, approval-mozilla-beta?, approval-mozilla-release?",
                            "attachment_id": 8417443,
                            "field_name": "flagtypes.name",
                            "removed": "",
                        }
                    ],
                    "when": "2014-05-05T20:25:06Z",
                    "who": "hurley@todesschaf.org",
                }
            ],
        )

    @responses.activate
    def test_search_landing(self):
        def commenthandler(bug, bugid, data):
            data["comments"] = bug["comments"]

        data = {}
        bugzilla.Bugzilla(
            656113, commenthandler=commenthandler, commentdata=data
        ).get_data().wait()

        central = bugzilla.Bugzilla.get_landing_comments(data["comments"], "central")
        self.assertEqual(len(central), 1)
        self.assertEqual(central[0]["revision"], "658a49b14bd6")
        self.assertEqual(
            central[0]["comment"],
            {
                    'text': 'Pushed by '
                            'geoff@darktrojan.net:\nhttps://hg.mozilla.org/comm-central/rev'
                            '/658a49b14bd6\nUse a grid in the editContactPanel. r=mkmelin',
                    'count': 7,
                    'id': 14974844,
                    'time': '2020-08-06T04:18:30Z',
                    'tags': [],
                    'bug_id': 656113,
                    'attachment_id': None,
                    'creation_time':
                        '2020-08-06T04:18:30Z',
                    'author': 'pulsebot@bots.tld',
                    'raw_text': 'Pushed by '
                                'geoff@darktrojan.net:\nhttps://hg.mozilla.org/comm-central/rev'
                                '/658a49b14bd6\nUse a grid in the editContactPanel. r=mkmelin',
                    'creator': 'pulsebot@bots.tld',
                    'is_private': False
            },
        )
        beta = bugzilla.Bugzilla.get_landing_comments(data["comments"], "beta")
        self.assertEqual(len(beta), 1)
        self.assertEqual(beta[0]["revision"], "7acaed666b89")
        self.assertEqual(
            beta[0]["comment"],
            {
                 'count': 11,
                 'text': 'Thunderbird '
                         '80.0b2:\nhttps://hg.mozilla.org/releases/comm-beta/rev/7acaed666b89',
                 'time': '2020-08-07T23:41:13Z',
                 'id': 14979145,
                 'tags': ['bugherder', 'uplift'],
                 'bug_id': 656113,
                 'creation_time': '2020-08-07T23:41:13Z',
                 'attachment_id': None,
                 'creator': 'rob@thunderbird.net',
                 'raw_text': 'Thunderbird 80.0b2:\nhttps://hg.mozilla.org/releases/comm-beta/rev/7acaed666b89',
                 'author': 'rob@thunderbird.net',
                 'is_private': False
            },
        )

        multiple = bugzilla.Bugzilla.get_landing_comments(
            data["comments"], ["beta", "central"]
        )
        self.assertEqual(
            multiple,
            [
                {
                    "revision": "658a49b14bd6",
                    "channel": "central",
                    "comment": {
                        'text': 'Pushed by '
                                'geoff@darktrojan.net:\nhttps://hg.mozilla.org/comm-central/rev'
                                '/658a49b14bd6\nUse a grid in the editContactPanel. r=mkmelin',
                        'count': 7,
                        'id': 14974844,
                        'time': '2020-08-06T04:18:30Z',
                        'tags': [],
                        'bug_id': 656113,
                        'attachment_id': None,
                        'creation_time':
                            '2020-08-06T04:18:30Z',
                        'author': 'pulsebot@bots.tld',
                        'raw_text': 'Pushed by '
                                    'geoff@darktrojan.net:\nhttps://hg.mozilla.org/comm-central/rev'
                                    '/658a49b14bd6\nUse a grid in the editContactPanel. r=mkmelin',
                        'creator': 'pulsebot@bots.tld',
                        'is_private': False
                    },
                },
                {
                    "revision": "7acaed666b89",
                    "channel": "beta",
                    "comment": {
                        'count': 11,
                        'text': 'Thunderbird '
                                '80.0b2:\nhttps://hg.mozilla.org/releases/comm-beta/rev'
                                '/7acaed666b89',
                        'time': '2020-08-07T23:41:13Z',
                        'id': 14979145,
                        'tags': ['bugherder', 'uplift'],
                        'bug_id': 656113,
                        'creation_time': '2020-08-07T23:41:13Z',
                        'attachment_id': None,
                        'creator': 'rob@thunderbird.net',
                        'raw_text': 'Thunderbird '
                                    '80.0b2:\nhttps://hg.mozilla.org/releases/comm-beta/rev'
                                    '/7acaed666b89',
                        'author': 'rob@thunderbird.net',
                        'is_private': False
                    },
                },
            ],
        )

        data = {}
        bugzilla.Bugzilla(
            1634963, commenthandler=commenthandler, commentdata=data
        ).get_data().wait()

        central = bugzilla.Bugzilla.get_landing_comments(data["comments"], "central")
        self.assertEqual(len(central), 6)


class BugAttachmentTest(MockTestCase):

    mock_urls = [bugzilla.Bugzilla.URL]

    @responses.activate
    def test_bugid(self):
        def bughandler(bug, data):
            data["bug"] = bug

        def commenthandler(bug, bugid, data):
            data["comment"] = bug["comments"]

        def historyhandler(bug, data):
            data["history"] = bug

        def attachmenthandler(bug, bugid, data):
            data["attachment"] = bug

        data = {}
        bugzilla.Bugzilla(
            12345,
            bughandler=bughandler,
            bugdata=data,
            commenthandler=commenthandler,
            commentdata=data,
            historyhandler=historyhandler,
            historydata=data,
            attachmenthandler=attachmenthandler,
            attachmentdata=data,
        ).get_data().wait()

        self.assertEqual(data["bug"]["id"], 12345)
        self.assertEqual(len(data["comment"]), 19)
        self.assertTrue(data["comment"][0]["text"].startswith(u"Steps to reproduce"))
        self.assertEqual(len(data["history"]["history"]), 24)
        self.assertEqual(len(data["attachment"]), 1)
        self.assertEqual(data["attachment"][0]["description"], "Some patch.")
        self.assertEqual(data["attachment"][0]["is_patch"], 1)
        self.assertEqual(data["attachment"][0]["is_obsolete"], 1)

    @responses.activate
    def test_search(self):
        def bughandler(bug, data):
            data["bug"] = bug

        def commenthandler(bug, bugid, data):
            data["comment"] = bug["comments"]

        def historyhandler(bug, data):
            data["history"] = bug

        def attachmenthandler(bug, bugid, data):
            data["attachment"] = bug

        data = {}
        bugzilla.Bugzilla(
            "bug_id=12345",
            bughandler=bughandler,
            bugdata=data,
            commenthandler=commenthandler,
            commentdata=data,
            historyhandler=historyhandler,
            historydata=data,
            attachmenthandler=attachmenthandler,
            attachmentdata=data,
        ).get_data().wait()

        self.assertEqual(data["bug"]["id"], 12345)
        self.assertEqual(len(data["comment"]), 19)
        self.assertTrue(data["comment"][0]["text"].startswith(u"Steps to reproduce"))
        self.assertEqual(len(data["history"]["history"]), 24)
        self.assertEqual(len(data["attachment"]), 1)
        self.assertEqual(data["attachment"][0]["description"], "Some patch.")
        self.assertEqual(data["attachment"][0]["is_patch"], 1)
        self.assertEqual(data["attachment"][0]["is_obsolete"], 1)

    @responses.activate
    def test_search_only_attachment(self):
        def bughandler(bug, data):
            data["bug"] = bug

        def attachmenthandler(bug, bugid, data):
            data["attachment"] = bug

        data = {}
        bugzilla.Bugzilla(
            "bug_id=12345",
            bughandler=bughandler,
            bugdata=data,
            attachmenthandler=attachmenthandler,
            attachmentdata=data,
        ).get_data().wait()

        self.assertEqual(data["bug"]["id"], 12345)
        self.assertEqual(len(data["attachment"]), 1)
        self.assertEqual(data["attachment"][0]["description"], "Some patch.")
        self.assertEqual(data["attachment"][0]["is_patch"], 1)
        self.assertEqual(data["attachment"][0]["is_obsolete"], 1)

    @responses.activate
    def test_attachment_include_fields(self):
        def attachmenthandler(bug, bugid, data):
            data["attachment"] = bug

        data = {}
        bugzilla.Bugzilla(
            12345,
            attachmenthandler=attachmenthandler,
            attachmentdata=data,
            attachment_include_fields=["description"],
        ).get_data().wait()

        self.assertEqual(data["attachment"][0]["description"], "Some patch.")
        self.assertNotIn("is_patch", data["attachment"][0])
        self.assertNotIn("is_obsolete", data["attachment"][0])

    @responses.activate
    def test_comment_include_fields(self):
        def commenthandler(bug, bugid, data):
            data["comments"] = bug["comments"]

        data = {}
        bugzilla.Bugzilla(
            12345,
            commenthandler=commenthandler,
            commentdata=data,
            comment_include_fields=["author"],
        ).get_data().wait()

        self.assertEqual(
            data["comments"][0]["author"], "marina@formerly-netscape.com.tld"
        )
        for field in [
            "bug_id",
            "creator",
            "raw_text",
            "id",
            "tags",
            "text",
            "is_private",
            "time",
            "creation_time",
            "attachment_id",
        ]:
            self.assertNotIn(field, data["comments"][0])


class BugDuplicateTest(MockTestCase):

    mock_urls = [bugzilla.Bugzilla.URL]

    @responses.activate
    def test_duplicate(self):
        self.assertEqual(
            bugzilla.Bugzilla.follow_dup([1244129, 890156]),
            {"1244129": "1240533", "890156": None},
        )

    @responses.activate
    def test_double_duplicate(self):
        self.assertEqual(bugzilla.Bugzilla.follow_dup([784349]), {"784349": "784345"})

    @responses.activate
    def test_not_duplicate(self):
        self.assertEqual(
            bugzilla.Bugzilla.follow_dup([890156, 1240533]),
            {"1240533": None, "890156": None},
        )


class User(MockTestCase):

    mock_urls = [bugzilla.BugzillaUser.URL]

    def __init__(self, a):
        tok = os.environ.get("API_KEY_BUGZILLA")
        if tok:
            bugzilla.BugzillaUser.TOKEN = tok
        super(User, self).__init__(a)

    @responses.activate
    def test_get_user(self):
        user = {}
        user_data = {}

        def user_handler(u, data):
            user.update(u)
            data.update(u)

        bugzilla.BugzillaUser(
            user_names="nobody@mozilla.org",
            user_handler=user_handler,
            user_data=user_data,
        ).wait()

        self.assertEqual(user["email"], "nobody@mozilla.org")
        self.assertEqual(user["name"], "nobody@mozilla.org")
        self.assertEqual(user["real_name"], "Nobody; OK to take it and work on it")
        self.assertEqual(user, user_data)

    @responses.activate
    def test_get_user_include_fields(self):
        user = {}
        user_data = {}

        def user_handler(u, data):
            user.update(u)
            data.update(u)

        bugzilla.BugzillaUser(
            user_names="nobody@mozilla.org",
            include_fields=["email", "real_name"],
            user_handler=user_handler,
            user_data=user_data,
        ).wait()

        self.assertEqual(user["email"], "nobody@mozilla.org")
        self.assertEqual(user["real_name"], "Nobody; OK to take it and work on it")
        self.assertNotIn("name", user)
        self.assertNotIn("id", user)
        self.assertEqual(user, user_data)

    @responses.activate
    def test_get_user_no_data(self):
        user = {}

        def user_handler(u):
            user.update(u)

        bugzilla.BugzillaUser(
            user_names="nobody@mozilla.org", user_handler=user_handler
        ).wait()

        self.assertEqual(user["email"], "nobody@mozilla.org")
        self.assertEqual(user["name"], "nobody@mozilla.org")
        self.assertEqual(user["real_name"], "Nobody; OK to take it and work on it")

    @responses.activate
    def test_get_user_id(self):
        user = {}

        def user_handler(u):
            user.update(u)

        bugzilla.BugzillaUser(user_names=1, user_handler=user_handler).wait()

        self.assertEqual(user["email"], "nobody@mozilla.org")
        self.assertEqual(user["name"], "nobody@mozilla.org")
        self.assertEqual(user["real_name"], "Nobody; OK to take it and work on it")

    @responses.activate
    def test_get_user_id_string(self):
        user = {}

        def user_handler(u):
            user.update(u)

        bugzilla.BugzillaUser(user_names="1", user_handler=user_handler).wait()

        self.assertEqual(user["email"], "nobody@mozilla.org")
        self.assertEqual(user["name"], "nobody@mozilla.org")
        self.assertEqual(user["real_name"], "Nobody; OK to take it and work on it")

    @responses.activate
    def test_get_user_array(self):
        user = {}

        def user_handler(u):
            user.update(u)

        bugzilla.BugzillaUser(
            user_names=["nobody@mozilla.org"], user_handler=user_handler
        ).wait()

        self.assertEqual(user["email"], "nobody@mozilla.org")
        self.assertEqual(user["name"], "nobody@mozilla.org")
        self.assertEqual(user["real_name"], "Nobody; OK to take it and work on it")

    @responses.activate
    def test_get_users(self):
        user = {"first": {}, "second": {}}

        def user_handler(u):
            if u["id"] == 1:
                user["first"].update(u)
            elif u["id"] == 208267:
                user["second"].update(u)
            else:
                raise Exception("Unexpected ID")

        bugzilla.BugzillaUser(
            user_names=["nobody@mozilla.org", "bugbot@bugzilla.org"],
            user_handler=user_handler,
        ).wait()

        self.assertEqual(user["first"]["email"], "nobody@mozilla.org")
        self.assertEqual(user["first"]["name"], "nobody@mozilla.org")
        self.assertEqual(
            user["first"]["real_name"], "Nobody; OK to take it and work on it"
        )
        self.assertEqual(user["second"]["email"], "bugbot@bugzilla.org")
        self.assertEqual(user["second"]["name"], "bugbot@bugzilla.org")
        self.assertEqual(user["second"]["real_name"], "bugbot on irc.mozilla.org")

    @responses.activate
    def test_get_users_ids(self):
        user = {"first": {}, "second": {}}

        def user_handler(u):
            if u["id"] == 1:
                user["first"].update(u)
            elif u["id"] == 208267:
                user["second"].update(u)
            else:
                raise Exception("Unexpected ID")

        bugzilla.BugzillaUser(
            user_names=["1", 208267], user_handler=user_handler
        ).wait()

        self.assertEqual(user["first"]["email"], "nobody@mozilla.org")
        self.assertEqual(user["first"]["name"], "nobody@mozilla.org")
        self.assertEqual(
            user["first"]["real_name"], "Nobody; OK to take it and work on it"
        )
        self.assertEqual(user["second"]["email"], "bugbot@bugzilla.org")
        self.assertEqual(user["second"]["name"], "bugbot@bugzilla.org")
        self.assertEqual(user["second"]["real_name"], "bugbot on irc.mozilla.org")

    @responses.activate
    def test_search_single_result(self):
        user = {}

        def user_handler(u):
            user.update(u)

        bugzilla.BugzillaUser(
            search_strings="match=nobody@mozilla.org", user_handler=user_handler
        ).wait()

        self.assertEqual(user["email"], "nobody@mozilla.org")
        self.assertEqual(user["name"], "nobody@mozilla.org")
        self.assertEqual(user["real_name"], "Nobody; OK to take it and work on it")

    @responses.activate
    def test_search_multiple_results(self):
        users = []

        def user_handler(u):
            users.append(u)

        bugzilla.BugzillaUser(
            search_strings="match=nobody", user_handler=user_handler
        ).wait()

        foundNobody1 = False
        foundNobody2 = False
        for user in users:
            if user["email"] == "nobody@mozilla.org":
                self.assertFalse(foundNobody1)
                foundNobody1 = True
                self.assertEqual(user["name"], "nobody@mozilla.org")
                self.assertEqual(
                    user["real_name"], "Nobody; OK to take it and work on it"
                )
            elif user["email"] == "attach-and-request@bugzilla.bugs":
                self.assertFalse(foundNobody2)
                foundNobody2 = True
                self.assertEqual(user["name"], "attach-and-request@bugzilla.bugs")
                self.assertEqual(
                    user["real_name"], "Nobody; OK to take it and work on it"
                )

        self.assertTrue(foundNobody1)
        self.assertTrue(foundNobody2)

    @responses.activate
    def test_search_multiple_queries(self):
        users = []

        def user_handler(u):
            users.append(u)

        bugzilla.BugzillaUser(
            search_strings=[
                "match=nobody@mozilla.org",
                "match=attach-and-request@bugzilla.bugs",
            ],
            user_handler=user_handler,
        ).wait()

        foundNobody1 = False
        foundNobody2 = False
        for user in users:
            if user["email"] == "nobody@mozilla.org":
                self.assertFalse(foundNobody1)
                foundNobody1 = True
                self.assertEqual(user["name"], "nobody@mozilla.org")
                self.assertEqual(
                    user["real_name"], "Nobody; OK to take it and work on it"
                )
            elif user["email"] == "attach-and-request@bugzilla.bugs":
                self.assertFalse(foundNobody2)
                foundNobody2 = True
                self.assertEqual(user["name"], "attach-and-request@bugzilla.bugs")
                self.assertEqual(
                    user["real_name"], "Nobody; OK to take it and work on it"
                )

        self.assertTrue(foundNobody1)
        self.assertTrue(foundNobody2)

    @responses.activate
    def test_get_nightly_version(self):
        nv = bugzilla.Bugzilla.get_nightly_version()
        self.assertEqual(nv, 81)


class BugLinksTest(unittest.TestCase):
    def test_bugid(self):
        self.assertEqual(
            bugzilla.Bugzilla.get_links("12345"), "https://bugzilla.mozilla.org/12345"
        )
        self.assertEqual(
            bugzilla.Bugzilla.get_links(12345), "https://bugzilla.mozilla.org/12345"
        )
        self.assertEqual(
            bugzilla.Bugzilla.get_links(["12345", "123456"]),
            [
                "https://bugzilla.mozilla.org/12345",
                "https://bugzilla.mozilla.org/123456",
            ],
        )
        self.assertEqual(
            bugzilla.Bugzilla.get_links([12345, 123456]),
            [
                "https://bugzilla.mozilla.org/12345",
                "https://bugzilla.mozilla.org/123456",
            ],
        )


if __name__ == "__main__":
    unittest.main()
