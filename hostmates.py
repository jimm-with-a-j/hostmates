import fire
import json
import requests
import itertools
import yaml

TAG_ENDPOINT = "/api/config/v1/autoTags/"
MZ_ENDPOINT = "/api/config/v1/managementZones/"
DB_ENDPOINT = "/api/config/v1/dashboards/"
DEFAULT_CONFIG_FILE = r"hostgroups.yaml"


class Main:

    # use the --config-file=... option to specify a different config file when running
    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        with open(config_file) as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
            self.token = config["apiToken"]
            self.tenant = config["tenant"]
            self.auth_header = {'Authorization': 'Api-Token {token}'.format(token=self.token),
                                'Content-Type': 'application/json'}
            self.delimiter = config["delimiter"]
            self.components = config["components"]
            self.combined_management_zones = config["combinedManagementZones"]

    def create_dashboards(self):
        print("Creating dashboards...")
        for entry in self.combined_management_zones:  # e.g. businessUnit_environment
            list_of_mzs = list(itertools.product(*self.create_list_of_lists_of_mz_values(entry)))
            for mz in list_of_mzs:
                with open("dashboard_template.json", "r") as template_json:
                    db_json = json.load(template_json)
                mz_name = '_'.join(mz)
                db_name = ' '.join(mz)
                db_json['dashboardMetadata']['name'] = db_name + " - Overview"

                # create the dashboards only if 1 management zone (id) matches the name
                mz_id_list = self.get_id_from_name(mz_name, self.tenant + MZ_ENDPOINT)
                if len(mz_id_list) > 1:
                    print("Multiple ids for management zone named {mz_name}...Skipping...".format(mz_name=db_name))
                if len(mz_id_list) == 1:
                    mz_id = mz_id_list[0]
                    db_json['dashboardMetadata']['dashboardFilter']['managementZone']['id'] \
                        = mz_id
                    print("Creating {db} dashboard...".format(db=db_name))
                    self.post_request(self.tenant + DB_ENDPOINT, db_json)

    def get_id_from_name(self, name, target):
        match_list = []
        comparison_list = self.get_request(self.tenant + MZ_ENDPOINT).json()['values']
        for config in comparison_list:
            if config['name'] == name:
                match_list.append(config['id'])
        if match_list == []:
            print("No id matches for name {name}".format(name=name))
        if len(match_list) > 1:
            print("Warning, multiple IDs match the name {name}".format(name=name))
        return match_list

    def create_management_zones(self):
        print("Creating management zones...")
        for entry in self.combined_management_zones:  # e.g. businessUnit_environment
            list_of_mzs = list(itertools.product(*self.create_list_of_lists_of_mz_values(entry)))
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

    def create_list_of_lists_of_mz_values(self, mz_definition):
        list_of_lists_of_mz_values = []
        for tag in mz_definition['components']:
            for component in self.components:
                if component['name'] == tag:
                    list_of_lists_of_mz_values.append(component["mzValues"])
        return list_of_lists_of_mz_values

    def create_tags(self):
        print("Creating tags...")
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
            response = requests.post(target, headers=self.auth_header, data=json.dumps(payload))
            assert (str(response.status_code).startswith("2"))
        except AssertionError as e:
            print("Non 200 response from API Call")
            print(response.content)
        finally:
            print(response.status_code)
            return response

    def get_request(self, target):
        try:
            response = requests.get(target, headers=self.auth_header)
            assert (str(response.status_code).startswith("2"))
        except AssertionError as e:
            print("Non 200 response from API Call")
            print(response.content)
        finally:
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
