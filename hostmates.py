import fire
import json
import requests
from config import Config
import itertools
import copy

TAG_ENDPOINT = "/api/config/v1/autoTags/"
MZ_ENDPOINT = "/api/config/v1/managementZones/"


class Main:

    def __init__(self):
        self.config = Config()
        self.components = self.config.components
        self.tenant = self.config.tenant
        self.delimiter = self.config.delimiter
        self.num_of_components = len(self.config.components)
        self.combined_management_zones = self.config.combined_management_zones

    def create_management_zones(self):
        for entry in self.combined_management_zones:  # e.g. businessUnit_environment
            arrays = []
            for tag in entry['components']:  # looking for the values for that tag (e.g. component)
                for component in self.components:
                    if component['name'] == tag:
                        arrays.append(component["mzValues"])  # adding to the array that holds each piece we need

            list_of_mzs = list(itertools.product(*arrays))  # creates list with all combinations
            for mz in list_of_mzs:
                with open("mz_template.json", "r") as template_json:
                    mz_json = json.load(template_json)
                i = 0
                while i < len(mz):
                    mz_json['rules'][0]['conditions'].append(create_condition_json(
                        entry['components'][i], mz[i]))
                    mz_json['rules'][1]['conditions'].append(create_condition_json(
                        entry['components'][i], mz[i]))
                    i = i + 1
                mz_name = '_'.join(mz)
                mz_json['name'] = mz_name
                print("Creating {mz} management zone...".format(mz=mz_name))
                self.post_request(self.tenant + MZ_ENDPOINT, mz_json)

    def create_tags(self):
        counter = 0
        for component in self.components:
            with open("tag_template.json", "r") as template_json:
                tag_json = json.load(template_json)

            tag_json['name'] = component['name']

            # if first entry in hostgroup
            if component['order'] == 1:
                tag_json['rules'][0]['valueFormat'] = "{{HostGroup:Name/^([^{delimiter}]++)}}" \
                    .format(delimiter=self.delimiter)
                tag_json['rules'][1]['valueFormat'] = "{{HostGroup:Name/^([^{delimiter}]++)}}" \
                    .format(delimiter=self.delimiter)

            # for other entries in hostgroup (except for last)
            if 0 < counter < self.num_of_components - 1:
                regex_start = ""
                for _ in range(component['order'] - 1):
                    regex_start += "[^_]+_"

                tag_json['rules'][0]['valueFormat'] = "{{HostGroup:Name/{regex_start}([^{delimiter}]++)}}" \
                    .format(delimiter=self.delimiter, regex_start=regex_start)
                tag_json['rules'][1]['valueFormat'] = "{{HostGroup:Name/{regex_start}([^{delimiter}]++)}}" \
                    .format(delimiter=self.delimiter, regex_start=regex_start)

            # for last entry in hostgroup
            if counter == self.num_of_components - 1:
                tag_json['rules'][0]['valueFormat'] = "{{HostGroup:Name/([^${delimiter}]++)$}}" \
                    .format(delimiter=self.delimiter)
                tag_json['rules'][1]['valueFormat'] = "{{HostGroup:Name/([^${delimiter}]++)$}}" \
                    .format(delimiter=self.delimiter)

            print("Creating {component} tag rule...".format(component=component))
            self.post_request(self.tenant + TAG_ENDPOINT, tag_json)
            counter = counter + 1

    def post_request(self, target, payload):
        try:
            response = requests.post(target, headers=self.config.auth_header, data=json.dumps(payload))
            assert (str(response.status_code).startswith("2"))
        except AssertionError as e:
            print("Non 200 response from API Call")
            print(response.content)
        finally:
            print(response.status_code)
            return response


def create_condition_json(key, value):
    condition_json = \
        {
            "key": {
                "attribute": "HOST_TAGS"
            },
            "comparisonInfo": {
                "type": "TAG",
                "operator": "EQUALS",
                "value": {
                    "context": "CONTEXTLESS",
                    "key": key,
                    "value": value
                },
                "negate": "false"
            }
        }

    return condition_json

if __name__ == '__main__':
    fire.Fire(Main)
