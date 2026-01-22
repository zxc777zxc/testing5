# PHPTRAVELS UI Automation Tests
Selenium + Pytest + pytest-html

# Overview

This project contains automated UI end-to-end tests for the website https://phptravels.net/
.
The tests are written in Python using Selenium WebDriver (Microsoft Edge) and Pytest, with rich HTML reporting provided by pytest-html.

The main goals of the project are:
  * Validate key user flows on the PHPTRAVELS website
  * Automatically capture screenshots of important steps and results
  * Generate a self-contained HTML report with:
    * screenshots
    * logs
    * test metadata
  * Make test execution and report viewing fully automated

# Implemented Test Scenarios

# 1. Visa Application
Open Visa section

Select source and destination countries

Search available visa options 

Fill in the visa submission form

Click Submit

Verify that the Submitted / Thank You page is displayed

Take a screenshot of the final result

# 2. Featured Hotel Booking
Open the main page

Select one of the Featured Hotels

Navigate to Rooms

Click Book Now

Fill in Personal Information

Fill Travellers Information (if visible)

Accept Terms & Conditions

Click Booking Confirm

Wait for the Invoice / Booking Result page

Take a screenshot of the invoice page

# 3. Popular Tour Booking
Open the Tours section

Select one of the Popular Tours     

Click Book Now     

Fill in booking and traveller information  

Accept Terms & Conditions  

Click Booking Confirm    

Wait for the Invoice / Booking Result page   

Take a screenshot of the invoice page

# Key Features
Selenium + Edge
  * Tests run in Microsoft Edge
  * Browser starts maximized
  * Page load timeout is configured
  * JavaScript clicks are used where needed for stability

Robust Helpers
  * Explicit waits (wait_present, wait_clickable, wait_visible)
  * Safe JavaScript clicks (js_click)
  * Automatic closing of bottom banners
  * Resilient checkbox handling for Terms & Conditions

Screenshots
  * Screenshots are taken via a dedicated shot() fixture
  * Each screenshot:
    * is saved to the screenshots/ directory
    * is embedded directly into the HTML report (base64)
  * Automatic screenshot is taken on test failure

Logging
  * Logging is enabled at INFO level
  * Logs are written to:
    * console (captured by pytest)
    * file: logs/test_run_<timestamp>.log
  * Logs are available in two ways:
    * directly inside the HTML report (Captured log)
    * as a clickable Log file link in the report

HTML Report
  * Generated using pytest-html
  * Fully self-contained (--self-contained-html)
  * Includes:
    * test results
    * screenshots
    * captured logs
    * environment metadata
  * Automatically opens in the browser after test execution


# Requirements
  * Python 3.10+
  * Microsoft Edge browser
  * Matching version of msedgedriver.exe
  * Installed Python packages:
    * pytest
    * selenium
    * pytest-html
