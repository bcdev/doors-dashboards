import unittest


from doors_dashboards.components.scatterplot import ScatterplotComponent

# from doors_dashboards.components.scatterplot import encode_main_group_dropdown
# from doors_dashboards.components.scatterplot import encode_group_dropdown
# from doors_dashboards.components.scatterplot import encode_xvar_dropdown
# from doors_dashboards.components.scatterplot import encode_yvar_dropdown
# from doors_dashboards.components.scatterplot import encode_linevar_dropdown
# from doors_dashboards.components.scatterplot import decode_main_group_dropdown
# from doors_dashboards.components.scatterplot import decode_group_dropdown


class EncoderTest(unittest.TestCase):

    def setUp(self) -> None:
        self.plot = ScatterplotComponent()

    def test_encode_decode_main_group_dropdown(self):
        self.assertEqual("maingroup_drp_option_erf",
                         self.plot.encode_main_group_dropdown("erf"))
        self.assertEqual("maingroup_drp_option_erf_arf",
                         self.plot.encode_main_group_dropdown("erf_arf"))
        self.assertEqual(
            "erf", self.plot.decode_main_group_dropdown("maingroup_drp_option_erf")
        )
        self.assertEqual(
            "erf_arf",
            self.plot.decode_main_group_dropdown("maingroup_drp_option_erf_arf")
        )

    def test_encode_decode_group_dropdown(self):
        self.assertEqual("group_drp_option_erf_arf",
                         self.plot.encode_group_dropdown("erf", "arf"))
        self.assertEqual("group_drp_option_erf-arf_ink-ank",
                         self.plot.encode_group_dropdown("erf_arf", "ink_ank"))
        collection, main_group = \
            self.plot.decode_group_dropdown("group_drp_option_erf_arf")
        self.assertEqual("erf", collection)
        self.assertEqual("arf", main_group)
        collection, main_group = \
            self.plot.decode_group_dropdown("group_drp_option_erf-arf_ink-ank")
        self.assertEqual("erf_arf", collection)
        self.assertEqual("ink_ank", main_group)

    def test_encode_xvar_dropdown(self):
        self.assertEqual("point_x_var_drop_down_id_erf",
                         self.plot.encode_xvar_dropdown("erf"))
        self.assertEqual("point_x_var_drop_down_id_erf_arf",
                         self.plot.encode_xvar_dropdown("erf_arf"))

    def test_decode_xvar_dropdown(self):
        self.assertEqual(
            "erf", self.plot.decode_xvar_dropdown("point_x_var_drop_down_id_erf")
        )
        self.assertEqual(
            "erf_arf",
            self.plot.decode_xvar_dropdown("point_x_var_drop_down_id_erf_arf")
        )

    def test_encode_yvar_dropdown(self):
        self.assertEqual("point_y_var_drop_down_id_erf",
                         self.plot.encode_yvar_dropdown("erf"))
        self.assertEqual("point_y_var_drop_down_id_erf_arf",
                         self.plot.encode_yvar_dropdown("erf_arf"))

    def test_decode_yvar_dropdown(self):
        self.assertEqual(
            "erf", self.plot.decode_yvar_dropdown("point_y_var_drop_down_id_erf")
        )
        self.assertEqual(
            "erf_arf",
            self.plot.decode_yvar_dropdown("point_y_var_drop_down_id_erf_arf")
        )

    def test_encode_linevar_dropdown(self):
        self.assertEqual("line_var_drop_down_id_erf",
                         self.plot.encode_linevar_dropdown("erf"))
        self.assertEqual("line_var_drop_down_id_erf_arf",
                         self.plot.encode_linevar_dropdown("erf_arf"))

    def test_decode_linevar_dropdown(self):
        self.assertEqual(
            "erf", self.plot.decode_linevar_dropdown("line_var_drop_down_id_erf")
        )
        self.assertEqual(
            "erf_arf",
            self.plot.decode_linevar_dropdown("line_var_drop_down_id_erf_arf")
        )
