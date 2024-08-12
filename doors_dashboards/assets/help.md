
Dashboards App
==============

The Dashboards Application offers users an accessible and appealing interface 
for browsing and analyzing varied datasets using interactive visualizations. 
The datasets that can be visualized with the Dashboards App are vector data, such as 
in-situ measurements.
Any such dataset within the Dashboards App is called a collection. 

The Dashboards Application is a collection of several dashboards.
Each dashboard consists of different elements - so far, each one at least of a map - 
and may handle different collections.
Other elements are typically plots that may help to gain further insight into a
collection.
The overview button in the top left brings up the available dashboards.

<!-- <img src="doors_dashboards/assets/_static/screenshot_dashboard_selection_pnl.png" 
alt="Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Dashboard](_static/screenshot_dashboard_selection_pnl.png)

Functionality
=============

The Dashboards App provides access to a range of functions such as weather forecasts, 
time series, scatter plots, point and line graphs, and trajectory displays. 
It allows for fast load times and smooth interactions, benefiting the overall experience 
for users.

The Base Map
------------

The Map is the one element that you may find in every dashboard.
It will either show locations from elements of one or more collections, 
or other specifically denoted locations.
To zoom, either use the buttons in the top right bar of the map (becomes visible on 
hovering) or your mouse wheel. 

<!-- <img src="doors_dashboards/assets/_static/screenshot_map_window_features.png" 
alt="Bulgaria Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Bulgaria Dashboard](_static/screenshot_map_window_features.png)

A dashboard visualizes data from the datasets on top of a basemap.
For zooming hover the mouse on map and the buttons in the top right corner will show 
up or the zooming function of your computer mouse.
In the upper left corner a legend to the mapped collection is available. 
To toggle the display of collections on the map, click a collection's name in the 
upper left corner.
Double-clicking will cause that only the selected collection is shown, another 
double-click brings up the other collections again.

<!-- <img src="doors_dashboards/assets/_static/screenshot_map_legend.png" 
alt="Legend Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Legend Dashboard](_static/screenshot_map_legend.png)

To change the map theme click on the `Settings` button on the top right of the app. 
`Carto Positron` is the default map theme applied.

<!-- <img src="doors_dashboards/assets/_static/screenshot_map_setting.png" 
alt="Settings Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Settings Dashboard](_static/screenshot_map_setting.png)

Plots
-----

When the dashboard offers also plots in addition to the map, you can switch between
collections via the drop-down menu `Collection`. 
If you choose a collection, the graphs will update to display the correct data for 
that selection. 

<!-- <img src="doors_dashboards/assets/_static/screenshot_collection_drp.png" 
alt="Collection exp Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Collection exp Dashboard](_static/screenshot_collection_drp.png)

If more than one variable is available within a selected collection, 
you may change the variable by using the drop-down menu `Variable` on the right side 
of dashboard in visualization area.

<!-- <img src="doors_dashboards/assets/_static/screenshot_variable_drp.png" 
alt="Variable exp Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Variable exp Dashboard](_static/screenshot_variable_drp.png)

In the time range plot, to view data for certain time periods, use the `Time range` 
option at the top of the graph. 
This will allow you to view selective data for the specified variable. 
The `Time Slider` at the bottom of the graph allows for seeing various periods of data 
by moving it left or right.

<!-- <img src="doors_dashboards/assets/_static/screenshot_time_range.png" 
alt="Time range Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Time range Dashboard](_static/screenshot_time_range.png)

Some dashboards will offer more than one plot, like this one who offers a line and a
scatter plot, to better allow to explore the data.

<!-- <img src="doors_dashboards/assets/_static/screenshot_georgia_dashboard.png" 
alt="Georgia Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Georgia Dashboard](_static/screenshot_georgia_dashboard.png)

If more than one cruise is available for a collection, 
you may change the cruise by using the drop-down menu `Cruise`.

<!-- <img src="doors_dashboards/assets/_static/screenshot_cruise_drp.png" 
alt="Cruise Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Cruise Dashboard](_static/screenshot_cruise_drp.png)

If more than one station is available for a selected cruise, 
you may change the station by using the drop-down menu `Station`. 

<!-- <img src="doors_dashboards/assets/_static/screenshot_station_drp.png" 
alt="Station Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Station Dashboard](_static/screenshot_station_drp.png)

The selected station will be highlighted on the map. 
Likewise, if you select a location on the map, the plots will be updated accordingly. 

<!-- <img src="doors_dashboards/assets/_static/screenshot_selected_station.png.png" 
alt="Selected Station Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Selected Station Dashboard](_static/screenshot_selected_station.png)

To adjust the variables displayed on the scatter plot, use the `X-Var` and `Y-Var` 
drop-down menus.
These allow you to select the variables you want to display on the X- and Y-axis, 
respectively. 
Once you make a selection, the scatter plot will update.

<!-- <img src="doors_dashboards/assets/_static/screenshot_xvar_drp.png" 
alt="Xvar Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Xvar Dashboard](_static/screenshot_xvar_drp.png)

For each plot, there is a button bar in the top right. 
You can download a graph as png by clicking on the camera button. 
There is also functionality to zoom in and out, reset axes, and to pan.

<!-- <img src="doors_dashboards/assets/_static/screenshot_graph_menu_highlight.png" 
alt="Graph Menu Dashboard" style="width:60em;display:block;margin-left:auto;
margin-right:auto"/> -->
![Graph Menu Dashboard](_static/screenshot_graph_menu_highlight.png)
