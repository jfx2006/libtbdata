import pickle
import unittest

from libtbdata.phabricator import PhabricatorPatch


class PhabricatorTest(unittest.TestCase):
    def test_import(self):
        """
        Simply import the library to check that all requirements are available
        """
        from libtbdata.phabricator import PhabricatorAPI  # noqa

        assert True

    def test_pickle_phabricatorpatch(self):
        pickle.dumps(PhabricatorPatch("123", "PHID-DIFF-xxx", "", "rev", []))
