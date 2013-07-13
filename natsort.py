#!/bin/env python
# ---------------------------------------------------------
# natsort.py: Natural string sorting.
# ---------------------------------------------------------

# By Seo Sanghyeon.  Some changes by Connelly Barnes & Spondon Saha

def try_int(s):
    "Convert to integer if possible."
    try: return int(s)
    except: return s

def natsort_key(s):
    "Used internally to get a tuple by which s is sorted."
    import re
    return map(try_int, re.findall(r'(\d+|\D+)', s))

def natcmp(a, b):
    "Natural string comparison, case sensitive."
    return cmp(natsort_key(a), natsort_key(b))

def natcasecmp(a, b):
    "Natural string comparison, ignores case."
    return natcmp(a.lower(), b.lower())

def natsort(seq, cmp=natcmp, reverse=False):
    "In-place natural string sort."
    if reverse:
        seq.sort(cmp, reverse=True)
    else:
        seq.sort(cmp)

def natsorted(seq, cmp=natcmp, reverse=False):
    "Returns a copy of seq, sorted by natural string sort."
    import copy
    temp = copy.copy(seq)
    natsort(temp, cmp, reverse)
    return temp

if __name__ == "__main__":
    print natsorted(['ver-1.3.12', 'ver-1.3.3', 'ver-1.2.5', 'ver-1.2.15', 'ver-1.2.3', 'ver-1.2.1'])
    print natsorted(['Team 101', 'Team 58', 'Team 30', 'Team 1'])

# vim:ts=4:sw=4:et
