"""
The :mod:`stan.data.data_parse` module is the data step parser for SAS-like language.
"""

from stan.data.data_lex import dataStepStmt
from stan.data.data_expr import RESERVED_KEYWORDS

def _id_convert(v_ls, data):
    """id convert changes variable ids to the Pandas format. Returns a converted string
    
    It iterates through list of tokens checking whether it is a reserved keyword
    or not.
    
    Parameters
    ----------
    
    v_ls : list of tokens
    data : the source Pandas DataFrame
    
    """
    var_stmt = []
    for el in v_ls:
        try: 
            if el.id not in RESERVED_KEYWORDS:
                var_stmt.append("%s%s" % (data, el.id)) #if the expr is an identifier
            else:
                var_stmt.append(el)
        except:
            var_stmt.append(el)
    return ''.join(var_stmt)

def _set_convert(v_ls, data):
    """set convert converts the set options to Pandas format. Returns a converted string.
        
    Parameters
    ----------
    
    v_ls : list of tokens
    data : the source Pandas DataFrame
    
    """
    # check all the keys...
    ss = v_ls['name'][0]
    for key in v_ls.keys():
        if key == 'rename':
            rename_ls = ",".join(["'%s':'%s'" % (x,y) for x,y in v_ls['rename']])
            ss += '.rename(columns={%s})' % (rename_ls)
        if key == 'drop':
            drop_ls = ",".join(["'%s'" % x for x in v_ls['drop']])
            ss += '.drop([%s],1)' % drop_ls
    ss = "%s=%s\n" % (data, ss)
    return ss

def _logic_id_convert(v_ls, data, cond = ''):
    """id convert changes variable ids to the Pandas format. Returns a converted string
    
    It iterates through list of tokens checking whether it is a reserved keyword
    or not.
    
    Parameters
    ----------
    
    v_ls : list of tokens
    data : the source Pandas DataFrame
    cond : the condition to be applied if applicable
    
    """
    var_stmt = []
    for el in v_ls:
        try: 
            if el.id not in RESERVED_KEYWORDS:
                if cond != '':
                    var_stmt.append("%s.ix[(%s),'%s']" % (data, cond, el.id[0])) #if the expr is an identifier
                else:
                    var_stmt.append("%s%s" % (data, el.id)) #if the expr is an identifier
            else:
                var_stmt.append(el)
        except:
            if el == '=' : el = '=='
            var_stmt.append(el)
    return "(%s)" % ''.join(var_stmt)
    
def _logic(v_ls, data, cond_list = []):
    """_logic converts tokens into pandas if statement
    
    It works through using np.where.
    
    Parameters
    ----------
    
    v_ls : list of tokens
    data : the source Pandas DataFrame
    cond_list : list of conditions
    
    """
    ss = ''
    var_list = []
    if 'l_cond' in v_ls.keys():
        # df.ix[(df['a']%2 ==0), 'a'] = df[(df['a']%2 ==0)]['a'] + 1 
        cond = _logic_id_convert(v_ls['l_cond'], data)
        cond_list.append(cond)
        cond_list = list(set(cond_list))
        
    if 'assign' in v_ls.keys():
        cond_ = " & ".join(["(~(%s))" % x for x in cond_list if x != cond and x != '']+[cond])
        if 'singleExpr' in v_ls['assign'].keys():
            stmt = v_ls['assign']                  
            var_stmt = _logic_id_convert(stmt[1:], data, cond=cond_)
            ss += "%s.ix[(%s), '%s'] = %s\n" % (data, cond_, stmt[0], var_stmt)
            var_list.append(stmt[0])
            #ss = "    %s.loc[i,'%s']=%s\n" % (data, stmt[0], var_stmt)
        else:
            for stmt in v_ls['assign']:
                var_stmt = _logic_id_convert(stmt[1:], data, cond = cond_)
                ss += "%s.ix[(%s), '%s'] = %s\n" % (data, cond_, stmt[0], var_stmt)
                var_list.append(stmt[0])
        
    if 'r_cond' in v_ls.keys() and len(v_ls['r_cond']) != 0:
        cond_ = " & ".join(["(~(%s))" % x for x in cond_list])
        for stmt in v_ls['r_cond']:
            if 'l_cond' in stmt.keys():
                ss += _logic(stmt, data, cond_list)
            elif 'assign' in stmt.keys():
                if 'singleExpr' in stmt['assign'].keys():
                    stmt = stmt['assign']                  
                    var_stmt = _logic_id_convert(stmt[1:], data, cond=cond_)
                    ss += "%s.ix[(%s), '%s'] = %s\n" % (data, cond_, stmt[0], var_stmt)
                    var_list.append(stmt[0])
                else:
                    for stmt in stmt['assign']:
                        var_stmt = _logic_id_convert(stmt[1:], data, cond = cond_)
                        ss += "%s.ix[(%s), '%s'] = %s\n" % (data, cond_, stmt[0], var_stmt)
                        var_list.append(stmt[0])
            
            else:
                if 'singleExpr' in stmt.keys():
                    var_stmt = _logic_id_convert(stmt[1:], data, cond=cond_)
                    ss += "%s.ix[(%s), '%s'] = %s\n" % (data, cond_, stmt[0], var_stmt)
                    var_list.append(stmt[0])
    
    v_ss = "["+','.join(["'"+x+"'" for x in list(set(var_list))])+"]"
    ss = """for el in %s:
    if el not in %s.columns:
        %s[el] = np.nan
""" % (v_ss, data, data) + ss        
    return ss
    
def _data_convert(v_ls, data):
    """data convert converts the data options to Pandas format. Returns a converted string.
        
    Parameters
    ----------
    
    v_ls : list of tokens
    data : the source Pandas DataFrame
    
    """
    datas = data
    for key in v_ls.keys():
        if key == 'rename':
            rename_ls = ",".join(["'%s':'%s'" % (x,y) for x,y in v_ls['rename']])
            datas += '.rename(columns={%s})' % (rename_ls)
        if key == 'drop':
            drop_ls = ",".join(["'%s'" % x for x in v_ls['drop']])
            datas += '.drop([%s],1)' % drop_ls
    return "%s=%s\n" % (data, datas) if data != datas else ""
           
def data_parse(cstr):
    """data_parse parses the string and returns a Pandas compatible string
    
    Parameters
    ----------
    
    cstr : string written in SAS-like language
    
    """
    inf = dataStepStmt.parseString(cstr)
    bd = inf.asDict()
    
    ss = ''
    data = bd['data']['name'][0]
    
    # looking through set options
    if len(bd['set'].keys()) == 0: 
        pass
    else: 
        set_str = _set_convert(bd['set'], data)
        ss = set_str

    # check all stmts   
    if 'stmt_groups' in bd.keys():
        for g_stmt in bd['stmt_groups']:
            if 'stmt' in g_stmt.keys():
                for stmt in g_stmt:
                    if 'fcall' in stmt.keys():
                        var_stmt = _id_convert(stmt[1:], 'x')
                        ss += "%s['%s']=%s.apply(lambda x: %s, axis=1)\n" % (data, stmt[0], data, var_stmt)
                    else:
                        var_stmt = _id_convert(stmt[1:], data)
                        ss += "%s['%s']=%s\n" % (data, stmt[0], var_stmt)
                        
            if 'saslogical' in g_stmt.keys():
                if len(g_stmt['saslogical']) == 1:
                    ss += _logic(g_stmt['saslogical'][0], data)
                else:
                    for stmt in g_stmt['saslogical']:                    
                        ss += _logic(stmt, data)
    
    # check data options
    if len(bd['data'].keys()) == 0: 
        pass
    else: 
        ss += _data_convert(bd['data'], data)
    return ss

