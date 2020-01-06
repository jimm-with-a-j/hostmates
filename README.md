# Hostmates
This is a tool that allows you to automatically make a number of configurations within your Dynatrace environment automatically. These configurations will be based on what is possible through the config API.

# Config file
All configuration is specified in a YAML config file (see below).
```
apiToken: <dtApiToken>
tenant: <tenantUrlWithoutTrailingSlash>
delimiter: _
components:
  - name: businessUnit
    order: 1
    mzValues:
      - ECOM
      - IT
  - name: tier
    order: 2
    mzValues:
      - APP
      - WEB
  - name: environment
    order: 3
    mzValues:
      - PROD
      - QA
combinedManagementZones:
  - components:
    - tier
    - environment
    - businessUnit
  - components:
    - tier
    - environment
  ```
  * Configurations
    - environment details: token and tenant (be sure token has read and write config permissions
    - delimeter: what character breaks up your hostgroup pieces? APP_PROD
    - components: what are the pieces and order of your hostgroup? The mzValues are used when creating management zones.
    - combinedManagementZones: what management zones would you like created?
      - Each component of a management zone must match one of the hostgroup components described above it. Each management zones will           look for the matching components and then create a management zone for each value and combination that you specify.
  # Usage
  The default value used for the configuration file is "hostgroups.yaml", this can be overridden. Running with 'apply-config' will result in tags, management zones, and dashboards being created.
  
  `py hostmates.py [--config-file=<custom_file_name>] apply-config`
  
  You can replace "apply-config" with any of the following to only run that portion of the process (e.g. only create tags)
  
  `py hostmates.py create-tags`
  * create-tags
  * create-management-zones
  * create-dashboards
  
# Example
Say we have our hostgroups defined with them containing the business unit (e.g. ECOM, IT), the tier (e.g. WEB, APP) and the environment (e.g. PROD, QA) all separated by an underscore. Defining the possible values for each component is not required but they will be used when creating the management zones.

We then want to create a management zone per business unit and environment (e.g. ECOM_PROD, ECOM_QA, IT_PROD, IT_QA. A configuration file to accomplish this would like like this:
```
apiToken: 273618216gsgfaTOKEN832gyuwer
tenant: https://myenvironment
delimiter: _
components:
  - name: businessUnit
    order: 1
    mzValues:
      - ECOM
      - IT
  - name: tier
    order: 2
    mzValues:
      - APP
      - WEB
  - name: environment
    order: 3
    mzValues:
      - PROD
      - QA
combinedManagementZones:
  - components:
    - businessUnit
    - environment
```
      
 
