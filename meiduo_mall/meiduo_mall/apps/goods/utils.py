


def get_beradcrumb(category):
    '''
    获取面包屑导航
    :param category: 类别对象
    :return: 返回类别
    '''
    beradcrumb = {
        'cat1':'',
        'cat2':'',
        'cat3':''
    }
    if category.parent == None:     # 一级
        beradcrumb['cat1'] = category
    elif category.subs.count() == 0:        #三级
        cat2 = category.parent
        beradcrumb['cat1'] = cat2.parent
        beradcrumb['cat2'] = cat2
        beradcrumb['cat3'] = category
    else:           # 二级
        beradcrumb['cat1'] = category.parent
        beradcrumb['cat2'] = category

    return beradcrumb
