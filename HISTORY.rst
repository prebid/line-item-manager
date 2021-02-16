=======
History
=======

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
