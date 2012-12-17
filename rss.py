#!/usr/bin/env python
import sys

def create_rss(search_url):
	# Check for valid TradeMe search URL.
	if not search_url.startswith("http://www.trademe.co.nz/Browse/SearchResults.aspx?"):
		print "Invalid URL: %s" % search_url
		return
	search = search_url[search_url.find("?")+1:]

	# Remove leading "&".
	if search.startswith("&"):
		search = search[1:]
	search_params = dict(x.split("=") for x in search.split("&"))

	# Build API URL.
	api_url = "http://api.trademe.co.nz/v1/Search/General.json?"

	if "searchString" in search_params:
		api_url += "&search_string=" + search_params["searchString"]

	if "searchregion" in search_params:
		api_url += "&region=" + search_params["searchregion"]

	if "cid" in search_params:
		api_url += "&category=" + search_params["cid"]

	if "buy" in search_params and search_params["buy"] == "now":
		api_url += "&buy=BuyNow"
	else:
		api_url += "&buy=All"

	if "condition" in search_params:
		api_url += "&condition=%s" % search_params["condition"].capitalize()

	if "pay" in search_params and search_params["pay"] == "paynow":
		api_url += "&pay=PayNow"
	else:
		api_url += "&pay=All"

	# TODO: Sort order

	# Print out API URL.
	print api_url

for arg in sys.argv[1:]:
	create_rss(arg)


