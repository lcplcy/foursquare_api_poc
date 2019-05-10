# POC for Foursquare Places API

The API endpoints here are proposed additions to the existing Places API.

## /<VENUE_ID>/ls-proposeedit

This endpoint seeks to improve the existing process between Foursquare and our partners.

Instead of sending data directly to the Foursquare database, this endpoint does an additional step of cleaning the
data sent with rules that can be tweaked and changed via a Google Spreadsheet [here](https://docs.google.com/spreadsheets/d/1lwCCOReOyZS2ZmU0wT1fzgtOMGT9OdaQqGyDnE1ASy8/edit#gid=0).

These rules are pre-defined by Foursquare.

Currently, this endpoint only supports the REPLACE function, where it will replace "value1" with "value2" in the "fieldname" parameters.   
