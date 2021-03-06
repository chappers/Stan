"""
The :mod:`stan.proc.proc_parse` module is the proc parser for SAS-like language.
"""

import re
import pkgutil

from stan.proc.proc_expr import RESERVED_KEYWORDS, PROC_
import stan.proc_functions as proc_func
from stan.proc.proc_sql import proc_sql

def proc_parse(cstr):
    """proc parse converts procedure statements to python function equivalents
    
    Parameters
    ----------
    
    v_ls : list of tokens
    
    Notes 
    -----
    
    ``data`` and ``output``/``out`` are protected variables.    
    If you wish to use a DataFrame as an argument, prepend ``dt_`` for the parser to interpret this correctly
    """
    
    # if cstr is in the form "proc sql" we won't pass tokens
    
    if re.match(r"^\s*proc\s*sql", cstr.strip(), re.IGNORECASE):
        return proc_sql(cstr.strip())    
    
    v_ls = PROC_.parseString(cstr)
    
    sls = []
    preprend = ''
        
    for ls in v_ls[1:]:        
        if len(ls[1:]) > 1:
            sls.append("%s=['%s']" % (ls[0], "','".join(ls[1:])))
        else:
            if ls[0].startswith('dt_') or ls[0] in ['data']: # hungarian notation if we want to use DataFrame as a variable
                sls.append("%s=%s" % (ls[0], ls[1]))
            elif ls[0] in ['output', 'out']:
                preprend += '%s=' % ls[1]
            else:
                sls.append("%s='%s'" % (ls[0], ls[1]))
                
    # try to find v_ls[0] in the `proc_func` namespace...
    f_name = v_ls[0].strip().lower()
    if f_name in [name for _, name, _ in pkgutil.iter_modules(proc_func.__path__)]: # is there a better way?
        func_name = "%s.%s" % (f_name, f_name)
    else:
        func_name = f_name
    
    return '%s%s(%s)' % (preprend, func_name, ','.join(sls)) # this statement is a bit dodgy



