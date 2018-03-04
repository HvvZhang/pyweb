# -*- coding: utf-8 -*-
import hashlib

def get_md5(url):
    # 如果是unicode
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__ == "__main__":
    # get_md5不接受unicode编码
    print(get_md5("http://jobbole.com".encode("utf8")))