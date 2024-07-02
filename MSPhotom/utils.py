# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 17:08:35 2024

@author: mbmad
"""

def datetonum(date: str):
    """
    Convert a date string in the format 'MM-DD-YY' to a numerical representation.

    Parameters
    ----------
    date : str
        Date string in the format 'MM-DD-YY'.

    Returns
    -------
    int
        Date in numerical format.

    """
    
    if len(date) != 8:
        return False
    if date[2] != "-" or date[5] != "-":
        return False
    mdyextract = [date[0:2], date[3:5], date[6:8]]
    if all(x.isdigit() for x in mdyextract):
        mdyextract = [int(i) for i in mdyextract]
        return ((mdyextract[1]) + (mdyextract[0]*40) + (mdyextract[2]*500))
    return False
    
def numtodate(numcode: int):
    assert isinstance(numcode, int), 'numtodate accepts integers only'
    y, d = divmod(numcode,500)
    m, d = divmod(d,40)
    return (str(m).zfill(2)+"-"+str(d).zfill(2)+"-"+str(y).zfill(2))