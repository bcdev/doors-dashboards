import unittest
import yaml

from doors_dashboards.dashboards.dashboard import create_dashboard


class DashboardTest(unittest.TestCase):

    def test_create_dashboard_1(self):
        with open("test_configs/config_with_geodb.yml", "r") as tc:
            config = yaml.safe_load(tc)
            dashboard = create_dashboard(config)
            dashboard.run(debug=True)

    def test_create_dashboard_2(self):
        with open("test_configs/meteogram_config.yml", "r") as tc:
            config = yaml.safe_load(tc)
            dashboard = create_dashboard(config)
            dashboard.run(debug=True)
