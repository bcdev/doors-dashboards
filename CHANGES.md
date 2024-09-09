## Changes in 0.3 (in development)

* Dashboard data can be updated
* Added dashboard descriptions
* Do not show consent dialog again after declining consent
* Fixed bug with collapsing scatterplots

## Changes in 0.2

### Functionalities

* Scattermap can show background layers
* Link to viewer is included
* More colors are used for traces in the scattermap
* Added help
* Polygons can be drawn on scatter map
* Added consent message

### Fixes

* Scatter Plot and Line Plot also work when no main group is present in the 
  collection
* Time Series can be created for collections without group label

### Dashboard Configurations

* Include more argo datasets
* Include more Marine Litter datasets
* Adjusted Moorings
* Romania Dashboards are enabled
* Added Dashboards for Georgia Cruises

## Changes in 0.1

Initial version. 
The application is started by running `doors_dashboards.landingpage.py`.
You need to specify a port under which the dashboards shall run.
Dashboards are specified in configuration files located in the `configs` folder.
Dashboards may be excluded from loading by stating them in `blocklist.txt` in 
that folder.
Visualisation Components of a dashboard are located in the 
`doors_dashboards.components` package.
They implement `doors_dashboards.core.dashboardcomponent.DashboardComponent`.
In addition to the dashboards, there is a home landing page, 
located under `doors_dashboards.home.py`.
    