from django.conf import settings
from django.core.files.storage import Storage

class FastDFSStorage(Storage):
    def __init__(self, fdfs_base_url = None):
        '''文件储存类的初始化方法'''
        # if not fdfs_base_url:
        #     self.fdfs_base_url = settings.FDFS_BASE_URL
        # self.fdfs_base_url = fdfs_base_url
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self,name,mode ='rb'):
        '''
        打开文件时被调用的
        :param name: 文件的路径
        :param mode: 文件的打开方式
        :return: None
        '''
        # 因为当前不是去打开某一个文件，所以这个方法目前无用，但是又不得不写
        pass

    def _save(self, name, content):
        '''
        文件保存时被调用
        :param name: 文件路径
        :param content: 文件的打开方式
        :return: None
        '''
        pass

    def url(self, name):
        '''
        返回文件的全路径。
        :param name: 文件路径
        :return: 文件的全路径  http://192.168.168.169:8888/group1/M00/00/00/CtM3BVnifxeAPTodAAPWWMjR7sE487.jpg
        '''

        return settings.FDFS_BASE_URL + name