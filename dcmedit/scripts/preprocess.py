# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

import os
import os.path

from config import ConfigClass


def dcm_pipeline(parameters, _dir='dicomedit_scripts'):
    des = open(os.path.join(_dir, parameters['project'] + '.des'), 'r').read()
    expr = os.path.splitext(parameters['input_file'])[0].split(os.sep)
    des = des.replace('project', str(parameters['project'].encode('utf-8'))[2:-1])
    des = des.replace('subject', str(parameters['subject'].encode('utf-8'))[2:-1])
    if f'gr-{ConfigClass.DCM_PROJECT}' in expr:
        expr = os.path.join(*expr[expr.index(f'gr-{ConfigClass.DCM_PROJECT}')])
    else:
        expr = os.path.join(*expr[expr.index(f'core-{ConfigClass.DCM_PROJECT}')])
    des = des.replace('session', str(expr.encode('utf-8'))[2:-1])
    parameters['anonymize_script'] = os.path.join(parameters['ext_dir'], f"{parameters['subject']}.des")
    with open(parameters['anonymize_script'], 'w') as f:
        f.write(str(des))
