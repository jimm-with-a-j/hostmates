import fire
import json
import requests
from config import Config

TAG_ENDPOINT = "/api/config/v1/autoTags/"
MZ_ENDPOINT = "/api/config/v1/managementZones/"

class Main:

    def __init__(self):
        self.config = Config()
        self.components = self.config.components
        self.tenant = self.config.tenant
        self.delimiter = self.config.delimiter
        self.num_of_components = len(self.config.components)
        self.mz_values = self.config.mz_values

    def create_management_zones(self):
        print(self.components)

    def create_tags(self):

        counter = 0
        for component in self.components:
            with open("tag_template.json", "r") as template_json:
                tag_json = json.load(template_json)

            tag_json['name'] = component['name']

            # if first entry in hostgroup
            if counter == 0:
                tag_json['rules'][0]['valueFormat'] = "{{HostGroup:Name/^([^{delimiter}]++)}}"\
                    .format(delimiter=self.delimiter)
                tag_json['rules'][1]['valueFormat'] = "{{HostGroup:Name/^([^{delimiter}]++)}}" \
                    .format(delimiter=self.delimiter)

            # for other entries in hostgroup (except for last)
            if 0 < counter < self.num_of_components - 1:
                regex_start = ""
                for _ in range(counter - 1):
                    regex_start += "[^_]+_"

                tag_json['rules'][0]['valueFormat'] = "{{HostGroup:Name/{regex_start}([^{delimiter}]++)}}"\
                    .format(delimiter=self.delimiter, regex_start=regex_start)
                tag_json['rules'][1]['valueFormat'] = "{{HostGroup:Name/{regex_start}([^{delimiter}]++)}}" \
                    .format(delimiter=self.delimiter, regex_start=regex_start)

            # for last entry in hostgroup
            if counter == self.num_of_components - 1:
                tag_json['rules'][0]['valueFormat'] = "{{HostGroup:Name/([^${delimiter}]++)$}}" \
                    .format(delimiter=self.delimiter)
                tag_json['rules'][1]['valueFormat'] = "{{HostGroup:Name/([^${delimiter}]++)$}}" \
                    .format(delimiter=self.delimiter)

            # with open("new_file.json", "w") as f:
            #     json.dump(tag_json, f)

            print("Creating {component} tag rule...".format(component=component))
            self.post_request(self.tenant + TAG_ENDPOINT, tag_json)
            counter = counter + 1

    def post_request(self, target, payload):
        try:
            response = requests.post(target, headers=self.config.auth_header, data=json.dumps(payload))
            assert(str(response.status_code).startswith("2"))
        except AssertionError as e:
            print("Non 200 response from API Call")
            print(response.content)
        finally:
            print(response.status_code)
            return response


if __name__ == '__main__':
    fire.Fire(Main)
