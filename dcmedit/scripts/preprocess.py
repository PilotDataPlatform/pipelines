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
