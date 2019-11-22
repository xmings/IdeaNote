# -*- coding: utf-8 -*-
import os, time
from datetime import datetime
from urlmark.regtool import Reg

'''
360和Chrome使用的是json书签文件，Firefox用的是sqlite书签库
'''
BOOKMARK_FILE_CONFIG = {
    '360se': {
        'local_json_file': '{INSTALL_HOME}\\..\\User Data\\Default\\Bookmarks',
        'local_DB_file': '',
        'server_json_file': '{INSTALL_HOME}\\..\\User Data\\Default\\{USERID32}\\Bookmarks',
        'server_DB_file': '{INSTALL_HOME}\\..\\User Data\\Default\\{USERID32}\\360sefav.dat'
        },
    'Chrome': {
        'local_json_file': '{LOCALAPPDATA}\\Google\\Chrome\\User Data\\Default\\Bookmarks',
        'local_DB_file': '',
        'server_json_file': '',
        'server_DB_file': '',
    },
    'Firefox': {
        'local_json_file': '',
        'local_DB_file': '{APPDATA}\Mozilla\Firefox\Profiles\{DEFAULT}\places.sqlite',
        'server_json_file': '',
        'server_DB_file': '{APPDATA}\Mozilla\Firefox\Profiles\{DEFAULT}\places.sqlite',
    },
}

def fetch_bookmark_info(brower):
    browers = Reg.fetch_browers()
    brower_info = {}
    for bm in BOOKMARK_FILE_CONFIG[brower]:
        bookmark_file_path = BOOKMARK_FILE_CONFIG[brower][bm]
        bookmark_file_type = 'db' if bm.find('DB') >= 0 else 'json'
        
        if bookmark_file_path == '':
            continue
        
        if bookmark_file_path.find('{INSTALL_HOME}') >= 0:
            install_home = browers[brower]
            bookmark_file_path = bookmark_file_path.replace('{INSTALL_HOME}', install_home)
            
        bookmark_file_path = bookmark_file_path.replace('{LOCALAPPDATA}', os.getenv('LOCALAPPDATA')).replace('{APPDATA}', os.getenv('APPDATA'))
        
        if bookmark_file_path.find('{USERID32}') >= 0:
            user_home = []
            current_dir = bookmark_file_path.split('{USERID32}')[0]
            for f in os.listdir(current_dir):
                fpath = os.path.join(current_dir, f)
                if os.path.isdir(fpath) and len(f) == 32:
                    mtime = os.path.getmtime(fpath)
                    if not user_home:
                        user_home = [f, mtime]
                    else:
                        if mtime > user_home[1]:
                            user_home = [f, mtime]
            bookmark_file_path = bookmark_file_path.replace('{USERID32}', user_home[0])
        
        if bookmark_file_path.find('{DEFAULT}') >= 0:
            user_home = []
            current_dir = bookmark_file_path.split('{DEFAULT}')[0]
            for f in os.listdir(current_dir):
                fpath = os.path.join(current_dir, f)
                if os.path.isdir(os.path.join(current_dir, f)) and f.endswith('.default'):
                    mtime = os.path.getmtime(fpath)
                    if not user_home:
                        user_home = [f, mtime]
                    else:
                        if mtime > user_home[1]:
                            user_home = [f, mtime]
            bookmark_file_path = bookmark_file_path.replace('{DEFAULT}', f)
                    
        if not os.path.exists(bookmark_file_path):
            continue
        modification_time = datetime.fromtimestamp(os.path.getmtime(bookmark_file_path))
        if brower_info:
            if modification_time > brower_info.get("modification_time"):
                brower_info["modification_time"] = modification_time
                brower_info["bookmark_file_path"] = bookmark_file_path
                brower_info["bookmark_file_type"] = bookmark_file_type
        else:
            brower_info = {
                "name": brower,
                "modification_time": modification_time,
                "bookmark_file_path": bookmark_file_path,
                "bookmark_file_type": bookmark_file_type
            }
        
    return brower_info

    
if __name__ == '__main__':
    for brower in Reg.fetch_browers():
        print(fetch_bookmark_info(brower))






