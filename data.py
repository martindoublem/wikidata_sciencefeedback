#!/usr/bin/env python3

import requests
import json
import pprint
from datetime import datetime

API_URL = "https://www.wikidata.org/w/api.php?"

pp = pprint.PrettyPrinter(indent=4)
pprint.sorted = lambda arg, *a, **kw: arg


with open('props.json') as p:
    props_dict = json.load(p)


class Wikidata:
    def __init__(self, entry):
        self.entry = entry
        self.entity = self.search_entry()
        self.info = self.get_entity_info(self.entity[1], True, True)

    def define_payload(self, action, language, query):
        payload = {
            'action': action,
            'format': 'json'
        }
        if isinstance(query, list):
            query = query[0]
        if action == 'wbsearchentities':
            payload['limit'] = 1
            payload['language'] = language
            payload['search'] = query
        if action == 'wbgetentities':
            payload['languages'] = language
            payload['sites'] = language + 'wiki'
            payload['ids'] = query
            payload['props'] = 'labels|claims|descriptions'
        if action == 'query':
            payload['prop'] = 'imageinfo'
            payload['titles'] = 'File:' + query
            payload['iiprop'] = 'url|size|mime'
        return payload

    def request_data(self, payload):
        r = requests.post(API_URL, payload)
        data = r.json()
        return data

    def search_entry(self):
        payload = self.define_payload('wbsearchentities', 'en', self.entry)
        data = self.request_data(payload)
        entities = data.get('search')
        label = entities[0].get('label') if entities else None
        entity = entities[0].get('id') if entities else None
        if not (entity and label):
            raise NoEntryFound
        return(label, entity)

    def get_entity_info(self, entity_id, description, claims_info):
        language = 'en'
        payload = self.define_payload('wbgetentities', language, entity_id)
        data = self.request_data(payload)
        entities = data.get('entities')
        entity = entities[entity_id] if entities else None

        info = {'id': entity_id}

        if entity:
            labels = entity.get('labels')
            if labels:
                info['label'] = labels.get(language).get('value')

            if description is True:
                info['description'] = entity.get('descriptions').get(language).get('value')

            if claims_info is True:
                claims = entity.get('claims')
                if claims:
                    claims_hr = {}
                    images = {}
                    for key, value in claims.items():
                        prop = props_dict[key]
                        if 'image' in prop:
                            file = self.get_claim(value)
                            image_i = self.get_image_info(file)
                            image = {'name': file, 'info': image_i}
                            images[prop] = image
                        else:
                            claims_hr[prop] = self.get_claim(value)
                info['images'] = images
                info['claims'] = claims_hr

            return info
        return

    def get_claim(self, claim):
        results = []
        for c in claim:
            datavalue = c.get('mainsnak').get('datavalue')
            c_type = datavalue.get('type')
            value = datavalue.get('value')
            if c_type == 'string':
                results.append(value)
            elif c_type == 'quantity':
                unit = value.get('unit')
                if unit == '1':
                    results.append(int(value.get('amount')))
                elif 'entity' in unit:
                    id = unit.split('/')[-1]
                    entity_info = self.get_entity_info(id, False, False)
                    results.append(str(int(value.get('amount'))) + " " + entity_info['label'])
                else:
                    print(datavalue)
            elif c_type == 'time':
                time = value.get('time')
                time = time[1:-1]
                if '-00' in time:
                    results.append(time[0:4])
                else:
                    results.append(datetime.fromisoformat(time))
            elif c_type == 'wikibase-entityid':
                id = value.get('id')
                entity_info = self.get_entity_info(id, False, False)
                if entity_info.get('label'):
                    results.append(entity_info['label'])
            elif c_type == 'monolingualtext':
                results.append(value.get('text'))
            else:
                print(c_type)
                print(datavalue)
        if len(results) == 1:
            return results[0]
        return results

    def get_image_info(self, file):
        payload = self.define_payload('query', 'en', file)
        data = self.request_data(payload)
        result = data.get('query')
        if result:
            page = result.get('pages').get('-1')
            image_info = page.get('imageinfo')[0]
            image_info.pop('descriptionurl', None)
            image_info.pop('descriptionshorturl', None)
            return image_info
        return


class NoEntryFound(Exception):
    pass


if __name__ == '__main__':
    lookup = input("Enter the publisher to look for: ")
    w = Wikidata(lookup)
    pp.pprint(w.info)
