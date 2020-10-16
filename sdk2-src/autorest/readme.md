# MachineLearningServices

> see https://aka.ms/autorest

This is an autorest configuration file for the SDK vNext effort. It is a modified
version of the file used for AzureML's ARM APIs, which is defined [here](https://github.com/Azure/azure-rest-api-specs/blob/master/specification/machinelearningservices/resource-manager/readme.md).

---

## Configuration

### Basic Information

These are the global settings for the Machine Learning Services API.

``` yaml
openapi-type: arm
tag: package-2020-06-01
```

### Tag: package-2020-06-01

These settings apply only when `--tag=package-2020-06` is specified on the command line.

```yaml $(tag) == 'package-2020-06-01'
input-file:
  - mfe.json
  - machineLearningServices.json
```
---

# Code Generation

## Swagger to SDK

This section describes what SDK should be generated by the automatic system.
This is not used by Autorest itself.

``` yaml $(swagger-to-sdk)
swagger-to-sdk:
  - repo: azure-sdk-for-net
  - repo: azure-sdk-for-go
  - repo: azure-sdk-for-python
  - repo: azure-sdk-for-js
  - repo: azure-sdk-for-node
  - repo: azure-cli-extensions
```

## C#

These settings apply only when `--csharp` is specified on the command line.
Please also specify `--csharp-sdks-folder=<path to "SDKs" directory of your azure-sdk-for-net clone>`.

``` yaml $(csharp)
csharp:
  azure-arm: true
  license-header: MICROSOFT_MIT_NO_VERSION
  namespace: Microsoft.Azure.Management.MachineLearningServices
  output-folder: $(csharp-sdks-folder)/src/Generated
  clear-output-folder: true
```

## Java

These settings apply only when `--java` is specified on the command line.
Please also specify `--azure-libraries-for-java-folder=<path to the root directory of your azure-libraries-for-java clone>`.

``` yaml $(java)
azure-arm: true
fluent: true
namespace: com.microsoft.azure.management.machinelearning.services
license-header: MICROSOFT_MIT_NO_CODEGEN
payload-flattening-threshold: 1
output-folder: $(azure-libraries-for-java-folder)/azure-mgmt-machinelearning/services
```

### Java multi-api

``` yaml $(java) && $(multiapi)
batch:
  - tag: package-2020-06-01
```
### Tag: package-2020-06-01 and java

These settings apply only when `--tag=package-2020-06-01 --java` is specified on the command line.
Please also specify `--azure-libraries-for-java=<path to the root directory of your azure-sdk-for-java clone>`.

``` yaml $(tag) == 'package-2020-06-01' && $(java) && $(multiapi)
java:
  namespace: com.microsoft.azure.management.machinelearningservices.v2020_06_01
  output-folder: $(azure-libraries-for-java-folder)/sdk/machinelearningservices/mgmt-v2020_06_01
regenerate-manager: true
generate-interface: true
```


## Multi-API/Profile support for AutoRest v3 generators

AutoRest V3 generators require the use of `--tag=all-api-versions` to select api files.

This block is updated by an automatic script. Edits may be lost!

``` yaml $(tag) == 'all-api-versions' /* autogenerated */
# include the azure profile definitions from the standard location
require: $(this-folder)/../../../profiles/readme.md

# all the input files across all versions
input-file:
  - $(this-folder)/Microsoft.MachineLearningServices/stable/2020-06-01/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/stable/2020-04-01/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/stable/2020-03-01/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/stable/2020-01-01/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/stable/2019-11-01/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/stable/2019-06-01/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/stable/2019-05-01/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/stable/2018-11-19/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/preview/2020-05-01-preview/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/preview/2020-04-01-preview/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/preview/2020-02-18-preview/machineLearningServices.json
  - $(this-folder)/Microsoft.MachineLearningServices/preview/2018-03-01-preview/machineLearningServices.json

```

If there are files that should not be in the `all-api-versions` set,
uncomment the  `exclude-file` section below and add the file paths.

``` yaml $(tag) == 'all-api-versions'
#exclude-file:
#  - $(this-folder)/Microsoft.Example/stable/2010-01-01/somefile.json
```