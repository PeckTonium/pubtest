# Engagement

This folder contains the tools needed for generating and delivering
customer energy insights.

## Data Generation

These projects are within the [insights](/engagement/insights) directory.

* [report_cards](/engagement/insights/python-library): A python
  library with the functions for processing energy and weather data to
  produce energy insights. Contains a wrapper function which calls the
  necessary library components to produce all of the insights needed
  for generating customer insights.
* [generate_json](/engagement/insights/emr/generate_json): An EMR job
  which can be run locally as a Spark app or deployed to AWS which
  generates the json files needed for customer energy insights in
  bulk. To run locally, execute `make run_local CAMPAIGN_ID=1` with
  the appropriate campaign ID.

## Email Content Generation

These projects are within the [email](/engagement/email) directory.
