def jsonPropt(astr):#给json内的键加上双引号
    return astr.replace("\\'",'"').replace("'",'"').replace('"{',"'{").replace('}"',"}'")