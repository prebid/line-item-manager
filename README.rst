=================
line-item-manager
=================


.. image:: https://img.shields.io/pypi/v/line_item_manager.svg
        :target: https://pypi.python.org/pypi/line_item_manager




Create and manage line items.


* Free software: Apache Software License 2.0
* Documentation: https://docs.prebid.org/tools/line-item-manager.html


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

Advanced Features
-----------------

1. Use a custom line item template
::

   # 1. save and edit a copy of the default line item template
   $ line_item_manager show template > my_template.yml

   # 2. edit my_template.yml; e.g. add geoTargeting to exclude locations

   # 3. create line items referencing your custom template
   $ line_item_manager create my_config.yml \
   --single-order \
   --template my_template.yml

2. Use a custom settings file
::

   # 1. save and edit a copy of the default settings
   $ line_item_manager show settings > my_settings.yml

   # 2. edit my_settings.yml; e.g. use a custom bidder code

   # 3. create line items referencing your custom settings
   $ line_item_manager create my_config.yml \
   --single-order \
   --settings my_settings.yml

3. Use a custom schema file
::

   # 1. save and edit a copy of the default schema
   $ line_item_manager show schema > my_schema.yml

   # 2. edit my_schema.yml; e.g. use a custom currency list

   # 3. create line items referencing your custom schema
   $ line_item_manager create my_config.yml \
   --single-order \
   --schema my_schema.yml

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

Configure access to Google Ad Manager
-------------------------------------

In order to use line-item-manager, you need to provide JSON private key file and configure access to your Google Ad manager account:

1. In Google API Console generate private key file for service account
2. In Google Ad Manager enable API access and create new services user with Administrator role.

See `detailed instructions <https://developers.google.com/ad-manager/api/authentication#oauth>`_ in documentation of GAM authentication.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _`config`: https://github.com/prebid/line-item-manager/blob/master/line_item_manager/conf.d/line_item_manager.yml
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
