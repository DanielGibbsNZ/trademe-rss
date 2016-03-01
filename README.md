TradeMe RSS
===========

Provides RSS feeds for search results on the online auction site TradeMe.
Very basic, and probably quite crude.

To use, just put the files on a webserver, and make sure it knows how to execute python scripts.

Requirements
------------
* [Requests](http://python-requests.org)
* [Requests-OAuthLib](https://requests-oauthlib.readthedocs.org/)

TradeMe Developer
-----------------

In order to use this script you will need to register an application with TradeMe; this can be done [here](https://www.trademe.co.nz/MyTradeMe/Api/DeveloperOptions.aspx). Once your application has been approved you will need to copy your consumer key and consumer secret into the script. You will then need to generate an OAuth token and OAuth secret (which can be done [here](http://developer.trademe.co.nz/api-overview/authentication/) and copy them into the script.
