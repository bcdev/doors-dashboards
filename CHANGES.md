## Changes in 0.1.1 (in development)

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
    