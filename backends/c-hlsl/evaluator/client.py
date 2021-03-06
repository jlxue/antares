# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import os
import urllib.request

def eval(kernel_path, **kwargs):
    if not os.environ.get('AGENT_URL', ''):
        print("Skip to evaluate performance: env_var `AGENT_URL` not defined (required: e.g. export AGENT_URL=<win10-ip-addr>)")
        exit(1)

    url_with_port = os.environ['AGENT_URL'].strip()
    if ':' not in url_with_port and not url_with_port.endswith('/'):
      url_with_port += ':8860'
    tune_agent_url = 'http://' + url_with_port
    with open(kernel_path, 'rb') as fp:
        kernel_data = fp.read()

    try:
      req = urllib.request.Request(tune_agent_url, headers={'ET': str(kwargs['expected_timeout'])}, data=kernel_data, method='PUT')
      with urllib.request.urlopen(req) as fp:
          output_content = fp.read().decode()
    except:
      raise Exception("Didn't get correct response from Antares Agent: Bad kernel code, or bad agent address?")

    start = output_content.find('\n- ')
    if start < 0:
      print(f"Evaluation Error: {output_content}")
      return {}
    stop = output_content.index('\n', start + 1)
    results = output_content[start + 3:stop].strip()
    results = json.loads(results)

    # Incorrect result, deny this result
    if 'K/0' not in results:
        results = {}
    for i in range(len(results)):
      key = 'K/%d' % i
      if key not in results:
        break
      results[key] = float('%.10e' % results[key])
    return results
