# custodian-ops-sam-tool
The [Custodian ops tool](https://github.com/cloud-custodian/cloud-custodian/blob/main/tools/ops/policylambda.py) that contains the Script required to transform the Custodian Policy to SAM template for Service catalog deployment. 

The Tool is modified as part of this sam tool that takes in the Custodian policy and IAM permissions yaml file to trasform the template into the SAM Template which contains both the IAM Role and Lambda function as Service Catalog Product. 

## Usage 

This script is being used part of the custodian sam to cfn convert codebuild stage where it takes the Custodian policy and converts it to Cloudformation SAM template with the IAM role wrapped part of the template. Some of the key pointers to consider when adding the custodian policy and permissions file 

1. Each custodian policy and its related permissions should be in a separate folder for e.g., encrypted-volumes , and the same name used for the policy-name.yml . 
2. Custodian policy IAM role should have a naming convention custodian-lambda-role-{{ PolicyName }} e.g., custodian-lambda-role-encrypted-volumes
3. The permissions.yml can have list of actions and resources in the below format , the PolicyName should be same as the one used for the folder and also for the policy-name.yml. 

```
PolicyName: "encrypted-volumes"
Permissions:
  - Action:
      - "ec2:Describe*"
      - "ec2:TerminateInstances"
    Resource:
      - "*"
  - Action:
      - "ec2:CreateTags"
      - "ec2:DeleteTags"
    Resource:
      - "*"
```
