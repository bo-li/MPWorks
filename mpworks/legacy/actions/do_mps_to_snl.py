import os
import traceback
from pymongo import MongoClient
import yaml
from mpworks.legacy.mps_to_snl import mps_dict_to_snl
from mpworks.snl_utils.snl_mongo import SNLMongoAdapter

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'May 08, 2013'


RESET = True

if __name__ == '__main__':

    module_dir = os.path.dirname(os.path.abspath(__file__))
    automation_f = os.path.join(module_dir, 'automation.yaml')
    snl_f = os.path.join(module_dir, 'snl.yaml')

    with open(automation_f) as f:
        y = yaml.load(f)

    mc = MongoClient(y['host'], y['port'])
    db = mc[y['db']]

    db.authenticate(y['username'], y['password'])

    snldb = SNLMongoAdapter.from_file(snl_f)
    if RESET:
        snldb._reset()

    for mps in db.mps.find(timeout=False):
        try:
            if RESET or not snldb.snl.find_one({"about._materialsproject.deprecated.mps_ids": mps['mps_id']}):
                snl = mps_dict_to_snl(mps)
                if snl:
                    snldb.add_snl(snl)
            else:
                print 'SKIPPING', mps['mps_id']
        except:
            traceback.print_exc()
            print 'ERROR - mps id:', mps['mps_id']

    print 'DONE'