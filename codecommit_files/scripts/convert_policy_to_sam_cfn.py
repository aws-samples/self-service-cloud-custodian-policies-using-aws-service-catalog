# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os 
import subprocess
import sys
import boto3
import logging
import botocore

# s3 boto3 client

s3_client = boto3.client('s3')

# Logging set level
logging.basicConfig(level = logging.INFO)


def convert_sam_to_cfn(SAM_DIR,policy_name,bucket_name, policy_version):
    """
    Convert SAM Template to CFN Template
    """
    os.chdir(SAM_DIR)
    policy_sam_file =  "sam-" + f"{policy_name}.yml"
    policy_cfn = f"{policy_name}.yml"

    logging.info(f"INFO - Packaging SAM Template and push to S3")
    
    cfn_package_cmd = [
        "aws", "cloudformation", "package",
        "--template-file", policy_sam_file,
        "--s3-bucket", bucket_name,
        "--output-template-file", policy_cfn,
        "--s3-prefix", f"custodian_policy_cfn_templates/{policy_name}",
        "--metadata", f"policy={policy_name},version={policy_version}"
    ]

    sys.stdout.flush()
    completion = subprocess.run(cfn_package_cmd, check=True) # nosec
    logging.info(f"INFO - {policy_name} Policy is successfully packaged SAM Template into Cloud Formation")

    # s3_cp_metadata = [
    #     "aws", "s3", "cp", 
    #     f"{policy_name}.yml",
    #     f"s3://{bucket_name}/custodian_policy_cfn_templates/{policy_name}/{policy_name}.yml",
    #     "--metadata", f"version={policy_version},policy={policy_name}"
    # ]

    # completion = subprocess.run(s3_cp_metadata, check=True) # nosec

    try:
        logging.info(f"INFO - Uploading file to Custodian templates bucket")
        policy_object_metadata = { 'policy': policy_name, 'version': policy_version }
        ExtraArgs = {'Metadata': policy_object_metadata}
        s3_client.upload_file(f"{policy_name}.yml", bucket_name, f"custodian_policy_cfn_templates/{policy_name}/{policy_name}.yml", ExtraArgs)

    except botocore.exceptions.ClientError as error:
        logging.error(f"The object upload failed due to {error}")
        raise error
    
def convert_policy_to_sam(policy_name, policyfile_path, policy_permissions):
    """
    Convert a policy file to SAM template and stores the policy files in the path /Build_DIR/<PolicyStakeHolder>/<Policyname>/policy_files/sam-<Policyname>.yaml
    """

    SAM_CODE = os.path.join('scripts', 'custodian-ops-sam-tool')
    sam_script = os.path.join(SAM_CODE, 'policylambda.py')
    iam_jinja = os.path.join(SAM_CODE, 'iam_wrapper.j2')
    SAM_DIR = os.path.join('scripts', 'sam-deploy')
    #SAM_DIR = '.'
    if not os.path.exists(SAM_DIR):
        os.makedirs(SAM_DIR)
    samcmd = [
        "python3",
        sam_script,
        '-c', policyfile_path,
        '-o', SAM_DIR,
        '-i', SAM_CODE,
        '-f', policy_permissions 
    ]
    logging.info(f"INFO - Converting policy {policy_name} to SAM Template...")
    sys.stdout.flush()
    logging.info(samcmd)
    completion = subprocess.run(samcmd) # nosec
    logging.info(completion)
    returncode = completion.returncode
    if returncode == 0:
        logging.info(f"INFO - {policy_name} Policy is successfully converted to SAM Template")
    else:
        logging.error(f"ERROR - {policy_name} Policy is failed to convert to the SAM Template")
    return SAM_DIR


def get_policy_version(custodian_bucket, policy_name):
    logging.info(f"Getting the policy version for {policy_name}")
    policy_object_exist = s3_client.list_objects_v2(Bucket=custodian_bucket, Prefix=f"custodian_policy_cfn_templates/{policy_name}")
    policy_version = '1'
    if policy_object_exist['KeyCount'] != 0:
        policy_object_content = s3_client.list_objects_v2(Bucket=custodian_bucket, Prefix=f"custodian_policy_cfn_templates/{policy_name}")
        for each_object in policy_object_content['Contents']:
            if ".yml" in each_object['Key']:
                policy_version_metadata = s3_client.head_object(Bucket=custodian_bucket,Key=each_object['Key'])
                policy_version = str(int(policy_version_metadata['Metadata']['version']) + 1)
    return policy_version

if __name__ == "__main__":
    policy_name = sys.argv[1]
    policyfile_path = sys.argv[2]
    policy_permissions = sys.argv[3]
    custodian_template_bucket = sys.argv[4]
    policy_version = get_policy_version(custodian_template_bucket,policy_name)
    logging.info(f"The policy version for the policy {policy_name} that is to be created is {policy_version}")
    SAM_DIR = convert_policy_to_sam(policy_name, policyfile_path, policy_permissions)
    convert_sam_to_cfn(SAM_DIR,policy_name,custodian_template_bucket, policy_version)
