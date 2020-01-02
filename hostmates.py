import fire
import json
import requests
from config import Config

TAG_ENDPOINT = "/api/config/v1/autoTags/"

class Main:

    def __init__(self):
        self.config = Config()
        self.components = self.config.components
        self.tenant = self.config.tenant
        self.delimiter = self.config.delimiter
        self.num_of_components = len(self.config.components)

    def create_tags(self):

        counter = 1
        for component in self.components:
            with open("tag_template.json", "r") as template_json:
                tag_json = json.load(template_json)

            tag_json['name'] = component

            # if first entry in hostgroup
            if counter == 1:
                tag_json['rules'][0]['valueFormat'] = "{{HostGroup:Name/^([^{delimiter}]++)}}"\
                    .format(delimiter=self.delimiter)
                tag_json['rules'][1]['valueFormat'] = "{{HostGroup:Name/^([^{delimiter}]++)}}" \
                    .format(delimiter=self.delimiter)

            # for other entries in hostgroup (except for last)
            if 1 < counter < self.num_of_components:
                regex_start = ""
                for _ in range(counter - 1):
                    regex_start += "[^_]+_"

                tag_json['rules'][0]['valueFormat'] = "{{HostGroup:Name/{regex_start}([^{delimiter}]++)}}"\
                    .format(delimiter=self.delimiter, regex_start=regex_start)
                tag_json['rules'][1]['valueFormat'] = "{{HostGroup:Name/{regex_start}([^{delimiter}]++)}}" \
                    .format(delimiter=self.delimiter, regex_start=regex_start)

            # for last entry in hostgroup
            if counter == self.num_of_components:
                tag_json['rules'][0]['valueFormat'] = "{{HostGroup:Name/([^${delimiter}]++)$}}" \
                    .format(delimiter=self.delimiter)
                tag_json['rules'][1]['valueFormat'] = "{{HostGroup:Name/([^${delimiter}]++)$}}" \
                    .format(delimiter=self.delimiter)

            # with open("new_file.json", "w") as f:
            #     json.dump(tag_json, f)

            self.post_request(self.tenant + TAG_ENDPOINT, tag_json)
            counter = counter + 1

    def post_request(self, target, payload):
        response = requests.post(target, headers=self.config.auth_header, data=json.dumps(payload))
        print(response.status_code)
        print(response.content)



if __name__ == '__main__':
    fire.Fire(Main)
