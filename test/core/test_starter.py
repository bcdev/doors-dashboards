from unittest import TestCase

from doors_dashboards.core.starter import list_dashboards


class StarterTest(TestCase):

    def test_list_dashboards(self):
        dashboards = list_dashboards()
        self.assertEqual(["ge1"], dashboards)
