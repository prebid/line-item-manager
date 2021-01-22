=================
line-item-manager
=================


.. image:: https://img.shields.io/pypi/v/line_item_manager.svg
        :target: https://pypi.python.org/pypi/line_item_manager




Create and manage line items.


* Free software: Apache Software License 2.0
* Documentation: https://line-item-manager.readthedocs.io.


Example Workflow
----------------

1. Save and edit a copy of the package config
::

   $ line_item_manager show config > my_config.yml

2. List bidder codes and names for reference
::

   $ line_item_manager show bidders

3. Do a dry run to see if everything looks right
::

   $ line_item_manager create my_config.yml \
   --dry-run \
   --private-key-file my_gam_creds.json \
   --network-code 12345678 \
   --network-name Publisher_GAM_Name \
   --bidder-code rubicon \
   --bidder-code ix

4. Do a test run creating a limited number of line items for visual inspection
::

   $ line_item_manager create my_config.yml \
   --test-run \
   --private-key-file my_gam_creds.json \
   --network-code 12345678 \
   --network-name Publisher_GAM_Name \
   --bidder-code rubicon \
   --bidder-code ix

5. Create line items
::

   $ line_item_manager create my_config.yml \
   --private-key-file my_gam_creds.json \
   --network-code 12345678 \
   --network-name Publisher_GAM_Name \
   --bidder-code rubicon \
   --bidder-code ix

Features
--------

* TODO

Local Development
-----------------

Installing and running line_item_manager locally using docker
::

   $ git clone git://github.com/prebid/line-item-manager
   $ cd line-item-manager
   $ command='line_item_manager' extra_args='--help' make docker-run

Configuration
-------------

See this default config_ that you can edit for your own purposes.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _`config`: https://github.com/prebid/line-item-manager/blob/master/line_item_manager/conf.d/line_item_manager.yml
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
