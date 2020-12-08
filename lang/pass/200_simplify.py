# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import os
import json
import itertools
import numpy as np
from common import backend, AntaresGlobal
from lang.einstein_v2 import walk_in_ast, OpTensor


def no_trivial_ax_input(ast_seq):
  for ast in ast_seq:
    ax_elim = []
    for ax in ast['props']['reduce_axes'] + ast['props']['data_axes']:
      if ax['range'] == 1:
        ax_elim.append(ax['name'])
    ast['props']['reduce_axes'] = [x for x in ast['props']['reduce_axes'] if x['name'] not in ax_elim]
    # ast['props']['data_axes'] = [x for x in ast['props']['data_axes'] if x['name'] not in ax_elim]
    if not ast['props']['reduce_axes']:
      ast['props']['reduce_type'] = None

    def scan_trivial_axis(root, ax_elim):
      if root._op == 'axis' and root._value in ax_elim:
        return OpTensor('const', 0, 'int32')
    walk_in_ast(ast['root'], scan_trivial_axis, [ax_elim], ast, 'root')

def update_global_dict(ast_seq, global_input_dict, global_output_dict):
  for ast in ast_seq:
    for k in ast['props']['input_dict']:
      if k in global_input_dict:
        global_input_dict[k] = ast['props']['input_dict'][k]
    k = ast['props']['output_name']
    if k in global_output_dict:
      global_output_dict[k] = {"shape": [x['range'] for x in ast['props']['data_axes']], "dtype": ast['root']._dtype}

def run_pass_v2(ast_seq, global_input_dict, global_output_dict):
  # Just a rough check
  if 'plan/' in os.environ.get('COMPUTE_V1', ''):
    return
  no_trivial_ax_input(ast_seq)
  update_global_dict(ast_seq, global_input_dict, global_output_dict)
