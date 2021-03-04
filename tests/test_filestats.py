# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

import six

from libtbdata import utils
from libtbdata.FileStats import FileStats


class FileStatsTest(unittest.TestCase):
    def test_filestats(self):
        path = "chat/protocols/matrix/matrix.jsm"
        info = FileStats(path).get_info()
        self.assertIsNotNone(info)
        self.assertEqual(info["path"], "chat/protocols/matrix/matrix.jsm")
        self.assertEqual(info["module"], "Instant Messaging")
        six.assertCountEqual(
            self,
            info["components"],
            [
                "Thunderbird:: Instant Messaging",
            ],
        )
        self.assertGreater(len(info["owners"]), 0)
        self.assertGreater(len(info["peers"]), 0)

    # def test_filestats_no_bugs(self):
    #     path = "LEGAL"
    #     info = FileStats(path).get_info()
    #     self.assertEqual(info["components"], set())
    #     self.assertIsNone(info["needinfo"])
    #     self.assertEqual(info["path"], path)
    #     self.assertEqual(len(info["guilty"]["patches"]), 1)
    #     self.assertEqual(info["guilty"]["main_author"], "hg@mozilla.com")
    #     self.assertEqual(info["guilty"]["last_author"], "hg@mozilla.com")
    #     self.assertNotIn("bugs", info)

    def test_filestats_date(self):
        path = "README.md"
        info = FileStats(path, utc_ts=utils.get_timestamp("today")).get_info()
        self.assertEqual(info["components"], set())
        self.assertIsNotNone(info["needinfo"])
        self.assertEqual(info["path"], path)
        self.assertIsNone(info["guilty"])

        info = FileStats(path, utc_ts=utils.get_timestamp("2019-08-14")).get_info()
        self.assertEqual(info["infered_component"], "Thunderbird::General")
        self.assertEqual(info["needinfo"], "ryan@thunderbird.net")
        self.assertEqual(info["path"], path)
        self.assertIsNone(info["guilty"])
        self.assertEqual(info["bugs"], 3)

        self.assertEqual(
            info, FileStats(path, utc_ts=utils.get_timestamp("2019-08-15")).get_info()
        )
        self.assertEqual(
            info, FileStats(path, utc_ts=utils.get_timestamp("2019-08-16")).get_info()
        )

        info = FileStats(
            path, utc_ts=utils.get_timestamp("2019-08-14")
        ).get_static_info()
        self.assertEqual(info["components"], set())
        self.assertIsNone(info["needinfo"])
        self.assertEqual(info["path"], path)
        self.assertIsNone(info["guilty"])
        self.assertNotIn("bugs", info)

        info = FileStats(path, utc_ts=utils.get_timestamp("2019-08-14")).get_info()
        self.assertEqual(info["infered_component"], "Thunderbird::General")
        self.assertEqual(info["needinfo"], "ryan@thunderbird.net")
        self.assertEqual(info["path"], path)
        self.assertIsNone(info["guilty"])
        self.assertEqual(info["bugs"], 3)


if __name__ == "__main__":
    unittest.main()
