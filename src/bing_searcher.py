#!/usr/bin/python

import json
import os
from pprint import pprint

import requests


class BingSearch:
    """
    Makes a call to the Bing Web Search API with a query and returns relevant web search.
    Documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-web-search/overview
    """
    def __init__(self, subscription_key:str=None) -> None:
        if subscription_key is None:
            if "AZURE_API_KEY" not in os.environ:
                raise Exception("AZURE_API_KEY must be declared in the environment. If you do not have one yet, please set up one in the Azure dashboard.")
            self.subscription_key = os.environ["AZURE_API_KEY"]
        else:
            self.subscription_key = subscription_key

        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"
        self.mkt = "en-US"

        if not self.is_api_key_valid():
            raise Exception("Invalid AZURE_API_KEY")

    # Construct a request
    def search(self, query:str):
        params = {"q": query, "mkt": self.mkt, "max-snippet": 10}
        headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}

        # Call the API
        try:
            response = requests.get(
                self.endpoint, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()
    
            return response.json()
        except Exception as ex:
            return None

    def is_api_key_valid(self):
        params = {"q": "", "mkt": self.mkt, "max-snippet": 10}
        headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}
        try:
            response = requests.get(
                self.endpoint, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()
        except Exception as ex:
            return False
        return True
