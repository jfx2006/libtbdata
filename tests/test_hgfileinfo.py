# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

import responses

from libtbdata import utils
from libtbdata.HGFileInfo import HGFileInfo
from libtbdata.hgmozilla import Mercurial
from tests.auto_mock import MockTestCase


class HGFileInfoTest(MockTestCase):
    mock_urls = [Mercurial.HG_URL]

    @responses.activate
    def test_hgfileinfo(self):
        path = "netwerk/protocol/http/nsHttpConnectionMgr.cpp"
        hi = HGFileInfo(path)
        fi = hi.get(path)

        self.assertIn("authors", fi)
        self.assertIsNotNone(fi["authors"])
        self.assertIn("bugs", fi)
        self.assertIsNotNone(fi["bugs"])

    # @responses.activate
    # def test_hgfileinfo_date(self):
    #     path = "LICENSE"
    #     hi = HGFileInfo(path)
    #
    #     fi = hi.get(path)
    #     self.assertEqual(len(fi["authors"]), 2)
    #     self.assertEqual(fi["authors"]["philringnalda@gmail.com"]["count"], 1)
    #     self.assertEqual(len(fi["authors"]["philringnalda@gmail.com"]["reviewers"]), 1)
    #     self.assertEqual(
    #         fi["authors"]["philringnalda@gmail.com"]["reviewers"]["gerv"], 1
    #     )
    #     self.assertEqual(fi["authors"]["hg@mozilla.com"]["count"], 1)
    #     self.assertEqual(fi["authors"]["hg@mozilla.com"]["reviewers"], {})
    #     self.assertEqual(fi["bugs"], set(["547914"]))
    #     self.assertEqual(len(fi["patches"]), 2)
    #     self.assertEqual(fi["patches"][0]["user"], "philringnalda@gmail.com")
    #     self.assertEqual(fi["patches"][1]["user"], "hg@mozilla.com")
    #
    #     fi = hi.get(path, utils.get_timestamp("2009-01-01"))
    #     self.assertEqual(len(fi["authors"]), 1)
    #     self.assertEqual(fi["authors"]["philringnalda@gmail.com"]["count"], 1)
    #     self.assertEqual(len(fi["authors"]["philringnalda@gmail.com"]["reviewers"]), 1)
    #     self.assertEqual(
    #         fi["authors"]["philringnalda@gmail.com"]["reviewers"]["gerv"], 1
    #     )
    #     self.assertEqual(fi["bugs"], set(["547914"]))
    #     self.assertEqual(len(fi["patches"]), 1)
    #     self.assertEqual(fi["patches"][0]["user"], "philringnalda@gmail.com")
    #
    #     fi = hi.get(
    #         path, utils.get_timestamp("2008-01-01"), utils.get_timestamp("2009-01-01")
    #     )
    #     self.assertEqual(fi["authors"]["hg@mozilla.com"]["count"], 1)
    #     self.assertEqual(fi["authors"]["hg@mozilla.com"]["reviewers"], {})
    #     self.assertEqual(fi["bugs"], set())
    #     self.assertEqual(len(fi["patches"]), 1)
    #     self.assertEqual(fi["patches"][0]["user"], "hg@mozilla.com")
    #
    #     fi = hi.get(path, utc_ts_to=utils.get_timestamp("2009-01-01"))
    #     self.assertEqual(len(fi["authors"]), 1)
    #     self.assertEqual(fi["authors"]["hg@mozilla.com"]["count"], 1)
    #     self.assertEqual(fi["authors"]["hg@mozilla.com"]["reviewers"], {})
    #     self.assertEqual(fi["bugs"], set())
    #     self.assertEqual(len(fi["patches"]), 1)
    #     self.assertEqual(fi["patches"][0]["user"], "hg@mozilla.com")
    #
    #     fi = hi.get(
    #         path, utils.get_timestamp("2006-01-01"), utils.get_timestamp("2007-01-01")
    #     )
    #     self.assertEqual(fi["authors"], {})
    #     self.assertEqual(fi["bugs"], set())
    #     self.assertEqual(fi["patches"], [])
    #
    #     fi = hi.get(
    #         path, utils.get_timestamp("2008-01-01"), utils.get_timestamp("2012-01-01")
    #     )
    #     self.assertEqual(len(fi["authors"]), 2)
    #     self.assertEqual(fi["authors"]["philringnalda@gmail.com"]["count"], 1)
    #     self.assertEqual(len(fi["authors"]["philringnalda@gmail.com"]["reviewers"]), 1)
    #     self.assertEqual(
    #         fi["authors"]["philringnalda@gmail.com"]["reviewers"]["gerv"], 1
    #     )
    #     self.assertEqual(fi["authors"]["hg@mozilla.com"]["count"], 1)
    #     self.assertEqual(fi["authors"]["hg@mozilla.com"]["reviewers"], {})
    #     self.assertEqual(fi["bugs"], set(["547914"]))
    #     self.assertEqual(len(fi["patches"]), 2)
    #     self.assertEqual(fi["patches"][0]["user"], "philringnalda@gmail.com")
    #     self.assertEqual(fi["patches"][1]["user"], "hg@mozilla.com")

    @responses.activate
    def test_hgfileinfo_creation_vs_push_date(self):
        path = "AUTHORS"
        hi = HGFileInfo(path, date_type="creation")

        fi = hi.get(path, utc_ts_to=utils.get_timestamp("2012-09-18"))
        self.assertEqual(len(fi["authors"]), 1)
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["count"], 1)
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["reviewers"], {})
        self.assertEqual(fi["bugs"], {'763623'})
        self.assertEqual(len(fi["patches"]), 1)
        self.assertEqual(fi["patches"][0]["user"], "gerv@gerv.net")

        fi = hi.get(path, utc_ts_to=utils.get_timestamp("2015-03-13"))
        self.assertEqual(len(fi["authors"]), 2)
        self.assertEqual(fi["authors"]["a.ahmed1026@gmail.com"]["count"], 1)
        self.assertEqual(len(fi["authors"]["a.ahmed1026@gmail.com"]["reviewers"]), 1)
        self.assertEqual(
            fi["authors"]["a.ahmed1026@gmail.com"]["reviewers"]["aleth"], 1
        )
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["count"], 1)
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["reviewers"], {})
        self.assertEqual(fi["bugs"], {'763623', '1050779'})
        self.assertEqual(len(fi["patches"]), 2)
        self.assertEqual(fi["patches"][0]["user"], "a.ahmed1026@gmail.com")
        self.assertEqual(fi["patches"][1]["user"], "gerv@gerv.net")

        hi = HGFileInfo(path, date_type="push")

        fi = hi.get(path, utc_ts_to=utils.get_timestamp("2012-09-18"))
        self.assertEqual(len(fi["authors"]), 1)
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["count"], 1)
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["reviewers"], {})
        self.assertEqual(fi["bugs"], {'763623'})
        self.assertEqual(len(fi["patches"]), 1)
        self.assertEqual(fi["patches"][0]["user"], "gerv@gerv.net")

        fi = hi.get(path, utc_ts_to=utils.get_timestamp("2015-03-13"))
        self.assertEqual(len(fi["authors"]), 2)
        self.assertEqual(fi["authors"]["a.ahmed1026@gmail.com"]["count"], 1)
        self.assertEqual(len(fi["authors"]["a.ahmed1026@gmail.com"]["reviewers"]), 1)
        self.assertEqual(
            fi["authors"]["a.ahmed1026@gmail.com"]["reviewers"]["aleth"], 1
        )
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["count"], 1)
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["reviewers"], {})
        self.assertEqual(fi["bugs"], {'763623', '1050779'})
        self.assertEqual(len(fi["patches"]), 2)
        self.assertEqual(fi["patches"][0]["user"], "a.ahmed1026@gmail.com")
        self.assertEqual(fi["patches"][1]["user"], "gerv@gerv.net")

    @responses.activate
    def test_hgfileinfo_author(self):
        path = "AUTHORS"
        hi = HGFileInfo(path)

        fi = hi.get(path, authors=["gerv@gerv.net"])
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["count"], 1)
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["reviewers"], {})
        self.assertEqual(fi["bugs"], {'763623'})
        self.assertEqual(len(fi["patches"]), 1)
        self.assertEqual(fi["patches"][0]["user"], "gerv@gerv.net")

        self.assertEqual(
            fi,
            hi.get(
                path,
                utils.get_timestamp("2012-01-01"),
                utils.get_timestamp("2013-01-01"),
                authors=["gerv@gerv.net"],
            ),
        )

        fi = hi.get(path, authors=["gerv@gerv.net", "arlolra@gmail.com"])
        self.assertEqual(len(fi["authors"]), 2)
        self.assertEqual(fi["authors"]["arlolra@gmail.com"]["count"], 1)
        self.assertEqual(len(fi["authors"]["arlolra@gmail.com"]["reviewers"]), 1)
        self.assertEqual(
            fi["authors"]["arlolra@gmail.com"]["reviewers"]["clokep"], 1
        )
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["count"], 1)
        self.assertEqual(fi["authors"]["gerv@gerv.net"]["reviewers"], {})
        self.assertEqual(fi["bugs"], {'763623', '1138689'})
        self.assertEqual(len(fi["patches"]), 2)
        self.assertEqual(fi["patches"][0]["user"], "arlolra@gmail.com")
        self.assertEqual(fi["patches"][1]["user"], "gerv@gerv.net")

    @responses.activate
    def test_hgfileinfo_multiple(self):
        path1 = "chat/protocols/matrix/matrix.jsm"
        path2 = "LICENSE"
        hi = HGFileInfo([path1, path2])
        fi1 = hi.get(path1)
        fi2 = hi.get(path2)

        self.assertIn("authors", fi1)
        self.assertIn("authors", fi2)
        self.assertIsNotNone(fi1["authors"])
        self.assertIsNotNone(fi2["authors"])
        self.assertIn("bugs", fi1)
        self.assertIn("bugs", fi2)
        self.assertIsNotNone(fi1["bugs"])
        self.assertIsNotNone(fi2["bugs"])


if __name__ == "__main__":
    unittest.main()
