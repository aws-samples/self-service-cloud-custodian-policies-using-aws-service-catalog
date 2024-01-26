# ucxar-sam-tool
The Nike UCX version of [Custodian ops tool](https://github.com/cloud-custodian/cloud-custodian/blob/main/tools/ops/policylambda.py) that contains the Script required to transform the Custodian Policy to SAM template for Service catalog deployment. 

The Tool takes in the Custodian policy and IAM permissions yaml file and trasforms the template into the SAM Template which contains both the IAM Role and Lambda function as Service Catalog Product. This Tool will be used as part of the [ucx policy generator build](https://github.com/nike-ucx/ucxar-cc-policies/blob/develop/build.py)

The SAM template supports a parameter called ```Actions``` which can be either Notify or Remediate if the Custodian Policy supports both the action , if not it supports only Notify if the Custodian Policy supports only the ```Notify``` action. 

## Usage 

Clone the repository

```
git clone git@github.com:nike-ucx/ucxar-sam-tool.git 

cd ucxar-sam-tool
```

Install Dependencies 

```
$ virtualenv ops_tool 
$ source ops_tool/bin/activate
$ pip install -r requirements.txt
```

To Transform the policy file to SAM template 

Pre-req 
* The file permissions.yml is present in the root in the below format 

```
PolicyName:
Permissions:
  - Action:
    - <list of IAM actions>
    Resource:
    - <list of resources to act upon>
  - Action:
    - <list of IAM actions>
    Resource:
    - <list of resources to act upon>
```

* The Custodian policy should be present in root folder as well. 

Run the following commands 

```
$ mkdir sam-deploy
$ python policylambda.py -o sam-deploy -c policies.yml -a notify (optional)

-a notify  to be passed only when the Policy supports only Notify. 

$ cd sam-deploy
$ aws cloudformation package --template-file policy_sam.yml --s3-bucket mybucket --output-template-file <policy name>.yml 
  --s3-prefix ServiceCatalogCodeuri   --metadata policy=<policy name>,PolicyStakeHolder=<policy stakholder>,version=1
```
