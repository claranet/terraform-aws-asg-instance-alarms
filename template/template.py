#!/usr/bin/env python

import decimal
import hashlib
import json
import sys


# Parse the query.
query = json.load(sys.stdin)

# Build the JSON template.

boolean_keys = [
    'ActionsEnabled',
]
decimal_keys = [
    'Threshold',
]
list_keys = [
    'AlarmActions',
    'Dimensions',
    'InsufficientDataActions',
    'OKActions',
]
long_keys = [
    'EvaluationPeriods',
    'Periods',
]

alarm = {}
for key, value in query.items():

    if key in boolean_keys:
        value = value.lower() in ('1', 'true')
    elif key in decimal_keys:
        value = decimal.Decimal(value)
    elif key in list_keys:
        value = json.loads(value)
    elif key in long_keys:
        value = long(value)

    if value:
        alarm[key] = value

source = json.dumps(alarm, indent=2, sort_keys=True)
etag = hashlib.sha256(source).hexdigest()

# Output the result to Terraform.
json.dump({
    'key': etag,
    'source': source,
    'etag': etag,
}, sys.stdout, indent=2)
sys.stdout.write('\n')
