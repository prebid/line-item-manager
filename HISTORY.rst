=======
History
=======

0.2.12 (2023-10-09)
-------------------
* Example script: Activate targeting values by network code, key Id and names (#149)

0.2.11 (2023-09-29)
-------------------
* Expanded currency list to include GAM currencies
* CLI support for custom settings and schema files for advanced users (#138)
* Upgraded PyYAML and googleads packages (#144)
* Python 3.11 support (#140)

0.2.10 (2023-08-30)
-------------------
* BUG FIX: Error for unsupported GAM API version is not handled properly (#116)
* BUG FIX: bidder-data.csv has spaces, causing line-item-manager to not find line items (#128)
* Update Google Ad Manager to v202308 (#129)

0.2.9 (2022-08-23)
-------------------
* Update Google Ad Manager to v202208 (#96)
* BUG FIX: tests expect 'oneVideo' to be a Prebid listed bidder (#109)
* Support size override for video (#111)

0.2.8 (2022-05-24)
-------------------
* BUG FIX: Specify CA certificates file when reading bidders data file (#104)
* Update Google Ad Manager to v202108 (#95)

0.2.7 (2022-05-17)
-------------------
* default creative duration to match max duration (that is currently 30000 milliseconds)
* support config duration in creative block

0.2.6 (2022-02-08)
-------------------
* Require Python >=3.7 (3.6 EOL DEC 23 2021)

0.2.5 (2022-02-08)
-------------------
* Update Google Ad Manager to v202105 (#93)
* Remove Python 3.6 and add 3.10 support (#91)
* Support for more line item types (sponsorship line item creation) (#86)
* BUG FIX: Certain currency values are invalid (#73)

0.2.4 (2021-12-01)
-------------------
* Update Google Ad Manager to v202102 (#63)
* Support Team ID (#77)
* Support LineItem.videoMaxDuration required in v202102 (#80)

0.2.3 (2021-05-26)
-------------------

* BUG FIX: datetime.timezone objects did not include zone name (#68)
* Support use of a custom line-item template (#65)
* Update bumpversion (depracated) and pytest-runner (out-of-date) (#62)

0.2.2 (2021-04-23)
-------------------

* Support reportableType settings for CustomTargetingKey (#55)
* Support for advertisers of different types (#48)
* BUG FIX: Custom targeting hb_bidder contains all key-values (#43)
* Upgrade jinja2 to 2.11.3 due to security vulnerabilities (#51)
* Upgrade PyYAML due to security vulnerabilities (#56)
* Remove requirements_dev.txt; not needed and introducing CVEs (#58)

0.2.1 (2021-02-23)
-------------------

* README includes steps to configure access to Google Ad Manager (#39)
* README includes link to prebid documentation (#40)

0.2.0 (2021-02-16)
-------------------

* Beta release

0.1.16 (2021-02-11)
-------------------

* BUG FIX: VAST URL should reference the 'uuid' targeting key in default template config (#32)
* Video creative duration set to 1 second to be consistent with Prebid documentation (#31)
* Custom targeting support for using 'IS_NOT' operator (#35)

0.1.15 (2021-02-09)
-------------------

* BUG FIX: Error during line item creative associaiton (#25)
* BIG FIX: Bidder Targeting Key status is 'INACTIVE' (#23)
* Added directory of helpful bin scripts (examples/bin) (#22)
* Added bin script (examples/bin/archive_order.py) for archiving orders (#21)

0.1.14 (2021-01-25)
-------------------

* CLI Help: noted that tests are not auto-archived

0.1.13 (2021-01-22)
-------------------

* First release to production PyPI
* Github action for publishing

0.1.12 (2021-01-12)
-------------------

* Support for Python 3.9
* Prebid and PrebidBidder classes added
* Type hints added
* Docstrings added
* Removed unused travis and tox support

0.1.11 (2020-12-17)
-------------------

* CLI option to display package version (#4)
* Schema invalidation of unrecognized config properties (#5)
* Support all bidder keys in config override map (#9)

0.1.10 (2020-12-15)
-------------------

* FEATURE: prebid recommended size override for banner creatives (#1)

0.1.9 (2020-12-11)
------------------

* BUG FIX: multi-line template assignments not parsed correctly (#2)

0.1.8 (2020-12-7)
------------------

* Support for including a custom line item priority.

0.1.7 (2020-12-4)
------------------

* Testing: Additional coverage.
* Conditional schema definitions.

0.1.6 (2020-12-3)
------------------

* Added 'Run of network' default inventory targeting
* Added predefined Prebid granularity types
* Dockerfile python change to slim from alpine

0.1.5 (2020-12-1)
------------------

* Fixed missing History.

0.1.4 (2020-12-1)
------------------

* Code cleanup. Deletion of unused code.
* Testing: Additional coverage.

0.1.3 (2020-11-30)
------------------

* Testing: Additional coverage.

0.1.2 (2020-11-29)
------------------

* Bug Fix: microAmount not properly assigned in line item
* Testing: Mock Ad Client and initial tests  

0.1.1 (2020-11-24)
------------------

* Auto-archive Orders on failure or interruption.

0.1.0 (2020-11-23)
------------------

* First release on Test PyPI.
