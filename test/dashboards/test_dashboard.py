import unittest
import yaml

from doors_dashboards.dashboards.dashboard import create_dashboard


class DashboardTest(unittest.TestCase):

    def test_create_dashboard_1(self):
        with open("test_configs/test_config1.yml", "r") as tc:
            config = yaml.safe_load(tc)
            dashboard = create_dashboard(config)
            dashboard.run_server(debug=True)

    def test_create_dashboard_2(self):
        with open("test_configs/test_config2.yml", "r") as tc:
            config = yaml.safe_load(tc)
            dashboard = create_dashboard(config)
            dashboard.run_server(debug=True)
