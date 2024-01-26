# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import sys
import subprocess

def validate_policy(policy_file):
    """
    Validate a policy file using the custodian tool.
    """
    print(f"INFO - Validating the Policy file: {policy_file}")
    sys.stdout.flush()
    completion = subprocess.run(['custodian', 'validate', policy_file]) # nosec
    returncode = completion.returncode
    if returncode == 0:
        print(f"INFO - Successfully Validated the Policy file: {policy_file}")
    else:
        print(f"ERROR - Failed to Validate the Policy file: {policy_file}")
    return returncode

if __name__ == "__main__":
    policy_file = sys.argv[1]
    validate_policy(policy_file)
