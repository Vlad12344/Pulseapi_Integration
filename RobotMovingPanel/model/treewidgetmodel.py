def selectTreeItem(item):
    items = {
        'TCP':      0,
        'Point':    2,
        'Program':  1,
        'Line':     3,
        'Plane':    4,
    }
    if item in items:
        return True, items[item]
    else: return False, 'Fail'