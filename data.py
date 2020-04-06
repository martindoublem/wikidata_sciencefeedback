#!/usr/bin/env python3

import wikipedia
import requests
import wikidata
import json

API_URL = "https://www.wikidata.org/w/api.php?"


class Wikidata:
    def __init__(self, entry):
        self.entry = entry
        self.entries = self.find_entries()
        self.entity = self.find_entity()

    def find_entries(self):
        return wikipedia.search(self.entry)

    def find_entity(self):
        for entry in self.entries:
            api_dict = {
                "action": "wbgetentities",
                "format": "json",
                "sites": "enwiki",
                "titles": entry,
                "props": "claims|labels",
                "languages": "en",
                "utf8": 1
            }
            api_request = requests.post(API_URL, data=api_dict)
            response_dict = api_request.json()
            entities = response_dict['entities']
            if len(list(entities.keys())) == 1:
                entity = list(entities.keys())[0]
            label = entities[entity]['labels']['en']['value']
            claims = entities[entity]['claims']
            


if __name__ == '__main__':
    lookup = input("Enter the publisher to look for: ")
    w = Wikidata(lookup)
