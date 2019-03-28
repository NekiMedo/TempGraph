# TempGraph
Create temperature graph for various geographical locations.

## Summary

* fetch weather data (JSON file) from Bureau of Meteorology (BOM) [web site](http://www.bom.gov.au/nsw/observations/nswall.shtml)
* extract temperature readings and append it to the data file; there's a separate data file for each location; locations are specified in the configuration file (locations.json by default)
* create temperature graph for the last few days (at most 7 days)
* if configured, push these graphs to the web server so it's available over the web; alternatively the graphs could be viewed locally in the `Graphs` directory by opening the `temperatures.html` file in the browser

## How to run
Normally this runs in a cron job, something like:

    ~~~~
	#min     hour         d1-31    m1-12   wday         script
     12       *            *        *       *           cd /home/user/proj/TempGraph && ./temp_graph.py
    ~~~~

There's a plan to make it run coninuously in the background (as a daemon) and fetch the data and generate graphs periodically.

## Other APIs
It started by processing weather data available from the **BOM** site but other APIs (OpenWeather) that support locations around the world are being considered.
