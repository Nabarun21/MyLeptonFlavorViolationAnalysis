import array

def binning(var):
    if var=='colmass':
        return array.array('d',(range(0,190,20)+range(215,470,35)+range(500,990,50)+range(1000,1520,100)))
    elif 'met' in var:
        return array.array('d',(range(0,190,20)+range(200,580,40)+range(600,1010,100)))
    elif 'pt' in var:
        return array.array('d',(range(0,190,20)+range(200,500,40)))
    else:
        raise("No binning found for "+var)
