'''
Created on 4 May 2017

@author: 
'''
import os
CUR_DIR = os.path.dirname(os.path.realpath(__file__))


def get_abs_path(key_inf='base_dir'):
    #utils_logger.debug(Const.info_getting_info_setting, key_inf)
    basedir = os.path.abspath(os.path.join(CUR_DIR, '..'))
    if (key_inf == 'base_dir'):
        return basedir
    else:
        return CUR_DIR


from tempfile import mkstemp
from shutil import move
from os import remove, close
def replace_in_file(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                if pattern in line:
                    new_file.write(subst + "\n")
                else:
                    new_file.write(line)
    close(fh)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
