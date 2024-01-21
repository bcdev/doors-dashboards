import unittest
import yaml

from doors_dashboards.dashboards.dashboard import create_dashboard


class DashboardTest(unittest.TestCase):

    def test_create_dashboard(self):
        with open("test_configs/test_config1.yml", "r") as tc:
            config = yaml.safe_load(tc)
            dashboard = create_dashboard(config)
            dashboard.run_server(debug=True)
