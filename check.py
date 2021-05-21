#!/usr/bin/env python3

import feedparser
import re
import sys
import config as cfg

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from slack_sdk.webhook import WebhookClient

webhook = WebhookClient(cfg.url)

# Fortinet RSS feed to parse.
feed = 'https://pub.kb.fortinet.com/rss/firmware.xml'

# For RSS entry filtering
past_hour = datetime.now() - timedelta(hours = 1)
past_day = datetime.now() - timedelta(days = 1)
past_week = datetime.now() - timedelta(days = 7)
past_month = datetime.now() - timedelta(days = 30)

d = feedparser.parse(feed)

# For future use.
products = []

for entry in d.entries:
    soup = BeautifulSoup(entry.description, 'html.parser')

    pattern = re.compile(r'^(.*?) and release notes')
    mo = pattern.search(soup.p.text)

    published_dt = datetime(*entry.published_parsed[:6], tzinfo=None)

    if not mo:
        # Perhaps in the future, put a slack webhook notification in here, instead.
        print("[!] Could not find any valid entries in the RSS feed!")
        sys.exit()

    # If entry date is newer than an hour... (prod = <, debug = >)
    if past_day < published_dt:
        message = f"{mo.group(1)} was posted at {entry.published}\n\n{entry.link}"
        response = webhook.send(text=message)
        print(f"Status: {response.status_code}")
        assert response.status_code == 200
        assert response.body == "ok"
