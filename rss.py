#!/usr/bin/env python
#
# rss.py
#
# Generates RSS feeds for TradeMe searches.
#
# Author: Daniel Gibbs
# Date: 31/01/2013
# Updated: 29/02/2016
#

import re
import sys
import json
import cgi
import time

from urllib import quote_plus, unquote_plus
from hashlib import md5

import requests
import requests_oauthlib

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
OAUTH_TOKEN = ""
OAUTH_SECRET = ""

trademe = requests_oauthlib.OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, resource_owner_key=OAUTH_TOKEN, resource_owner_secret=OAUTH_SECRET)

# Output an RSS feed for a given TradeMe search URL.
# Uses the TradeMe API which has limitations on how many calls can be made per hour.
def create_rss(search_url, dont_show_relistings):
	# Check for valid TradeMe search URL.
	# TODO: Support vehicle, job, house search etc.
	if not re.match("^http[s]?://www\.trademe\.co\.nz/Browse/SearchResults\.aspx\?.*", search_url):
		print "Location: index.html"
		print
		return
	search = search_url[search_url.find("?")+1:]

	# Remove leading "&" and create a dict of search parametres.
	if search.startswith("&"):
		search = search[1:]
	search_params = dict(x.split("=") for x in search.split("&"))

	# Start creating API URL and query string.
	api_url = "https://api.trademe.co.nz/v1/Search/General.json?expired=false"

	# There's no point trying to create an RSS feed if there's no search string.
	if "searchString" in search_params:
		api_url += "&search_string=" + search_params["searchString"]
	else:
		print "Location: index.html"
		print
		return

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

	if "sort_order" in search_params:
		if search_params["sort_order"] == "feature_first":
			api_url += "&sort_order=Default"
		elif search_params["sort_order"] == "price_asc":
			api_url += "&sort_order=PriceAsc"
		elif search_params["sort_order"] == "price_desc":
			api_url += "&sort_order=PriceDesc"
		elif search_params["sort_order"] == "buynow_asc":
			api_url += "&sort_order=BuyNowAsc"
		elif search_params["sort_order"] == "buynow_desc":
			api_url += "&sort_order=BuyNowDesc"
		elif search_params["sort_order"] == "bids_asc":
			api_url += "&sort_order=BidsMost"
		elif search_params["sort_order"] == "expiry_desc":
			api_url += "&sort_order=ExpiryDesc"
		elif search_params["sort_order"] == "expiry_asc":
			api_url += "&sort_order=ExpiryAsc"
		elif search_params["sort_order"] == "title_asc":
			api_url += "&sort_order=TitleAsc"

	# Perform the API call.
	search_result = trademe.get(api_url).json()
	# TODO: Check status of the API call result.

	# Output the RSS header and feed description.
	print "Content-Type: application/xml"
	print
	print "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
	print "<rss version=\"2.0\">"
	print "<channel>"
	print "<title>TradeMe search for %s</title>" % unquote_plus(search_params["searchString"])
	print "<link>%s</link>" % quote_plus(search_url)
	print "<description>TradeMe search for %s</description>" % search_params["searchString"]
	print "<language>en-nz</language>"
	print "<image>"
	print "<url>http://www.trademe.co.nz/images/iphonelogo.png</url>"
	print "<title>TradeMe Logo</title>"
	print "<link>%s</link>" % quote_plus(search_url)
	print "</image>"

	# For each item in the search result, output the RSS feed entry.
	try:
		for item in search_result["List"]:
			print "<item>"
			print "<title>%s</title>" % cgi.escape(item["Title"])
			print "<link>http://www.trademe.co.nz/Browse/Listing.aspx?id=%s</link>" % item["ListingId"]
			print "<description>"
			if "PictureHref" in item:
				print cgi.escape("<img src=\"%s\" title=\"%s\" />" % (item["PictureHref"], item["Title"]))
			print cgi.escape("<p>")
			if "Suburb" in item and "Region" in item:
				print cgi.escape("<strong>Location: </strong>%s, %s<br />" % (item["Suburb"], item["Region"]))
			print cgi.escape("<strong>Closes: </strong>%s<br />" % time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime(float(item["EndDate"][6:-2])/1000)))
			print cgi.escape("</p>")
			print cgi.escape("<p>");
			if "StartPrice" in item:
				print cgi.escape("<strong>Start Price: </strong>$%.2f<br />" % item["StartPrice"])
			if "BuyNowPrice" in item:
				print cgi.escape("<strong>Buy Now Price: </strong>$%.2f<br />" % item["BuyNowPrice"])
			if "MaxBidAmount" in item:
				print cgi.escape("<strong>Current Bid: </strong>$%.2f<br />" % item["MaxBidAmount"])
			print cgi.escape("</p>");

			if "IsReserveMet" in item:
				if item["IsReserveMet"]:
					print cgi.escape("<strong>Reserve Met</strong><br />")
				else:
					if not "HasReserve" in item or not item["HasReserve"]:
						print cgi.escape("<strong>No Reserve</strong><br />")
					else:
						print cgi.escape("<strong>Reserve Not Met</strong><br />")
			else:
				if not "HasReserve" in item or not item["HasReserve"]:
					print cgi.escape("<strong>No Reserve</strong><br />")

			print "</description>"
			print "<pubDate>%s</pubDate>" % time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(float(item["StartDate"][6:-2])/1000))
			if "CategoryName" in item:
				print "<category>%s</category>" % cgi.escape(item["CategoryName"])
			if dont_show_relistings:
				print "<guid>%s</guid>" % md5(item["Title"]).hexdigest()
			else:
				print "<guid>%s</guid>" % item["ListingId"]
			print "</item>"
	except Exception as e:
		sys.stderr.write("%s\n" % str(e))

	print "</channel>"
	print "</rss>"

# Get the TradeMe search URL from the request and output an RSS feed.
form = cgi.FieldStorage()
search_url = form.getfirst('url', '')
dont_show_relistings = form.getfirst('relistings', '')
create_rss(search_url, dont_show_relistings)
