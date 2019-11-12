import requests
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, quote, unquote
import xml.etree.ElementTree as et
from dateutil import parser
import os
import json


@dataclass
class File(object):
    href: str
    status: bool
    last_modified_time: datetime
    content_length: int
    etag: str
    content_type: str
    creation_time: datetime


@dataclass
class Directory(object):
    href: str
    status: bool
    last_modified_time: datetime
    content_length: int
    quota_used_bytes: int
    quota_available_bytes: int
    creation_time: datetime


class MyWebDav(object):
    def __init__(self, url, user, password):
        self.url = url  # https://dav.box.com/dav
        self.user = user
        self.password = password
        self.session = requests.Session()

    def _url_join(self, *path):
        url = self.url if self.url.endswith("/") else self.url + "/"

        for i in path:
            url += i.strip("/") + "/"
        return url.rstrip("/")

    def _parse_reponse(self, xml):
        href = xml.findtext('.//{DAV:}href')
        last_modified_time = xml.findtext('.//{DAV:}propstat/{DAV:}prop/{DAV:}getlastmodified')
        content_length = xml.findtext('.//{DAV:}propstat/{DAV:}prop/{DAV:}getcontentlength')
        creation_time = xml.findtext('.//{DAV:}propstat/{DAV:}prop/{DAV:}creationdate')
        resource_type = xml.find('.//{DAV:}propstat/{DAV:}prop/{DAV:}resourcetype/{DAV:}collection')
        status_text = xml.findtext('.//{DAV:}propstat/{DAV:}status')
        # print(resource_type)
        if resource_type is None:
            etag = xml.findtext('.//{DAV:}propstat/{DAV:}prop/{DAV:}getetag')
            content_type = xml.findtext('.//{DAV:}propstat/{DAV:}prop/{DAV:}getcontenttype')
            return File(
                href=unquote(href),
                status=True if status_text.find("200 OK") >= 0 else False,
                last_modified_time=parser.parse(last_modified_time),
                content_length=int(content_length),
                etag=etag,
                content_type=content_type,
                creation_time=parser.parse(creation_time)
            )

        quota_used_bytes = xml.findtext('.//{DAV:}propstat/{DAV:}prop/{DAV:}quota-used-bytes')
        quota_available_bytes = xml.findtext('.//{DAV:}propstat/{DAV:}prop/{DAV:}quota-available-bytes')

        return Directory(
            href=unquote(href),
            status=True if status_text.find("200 OK") >= 0 else False,
            last_modified_time=parser.parse(last_modified_time),
            content_length=int(content_length),
            quota_used_bytes=int(quota_used_bytes),
            quota_available_bytes=int(quota_available_bytes),
            creation_time=parser.parse(creation_time)
        )

    def list(self, path=""):
        resp = self.session.request(
            'PROPFIND', f"{self._url_join(path)}", auth=(self.user, self.password))
        if resp.ok:
            for xml in list(et.fromstring(resp.text)):
                yield self._parse_reponse(xml)
        raise Exception(resp.text)

    def upload(self, remote_dir, file, file_name=None):
        file_name = file_name if file_name else os.path.basename(file.name)
        resp = self.session.request(method="PUT",
                                    url=self._url_join(remote_dir, file_name),
                                    auth=(self.user, self.password),
                                    data=file.read()
                                    )
        print(resp.ok, resp.text)

    def info(self, remote_path):
        resp = self.session.request(method="PROPFIND",
                                    url=self._url_join(remote_path),
                                    auth=(self.user, self.password)
                                    )
        print(self._parse_reponse(et.fromstring(resp.text)))

    def download(self, remote_file):
        resp = self.session.request(method="GET",
                                    url=self._url_join(remote_file),
                                    auth=(self.user, self.password)
                                    )

        print(resp.ok)
        with open("d:\\cde.png", "wb") as f:
            f.write(resp.content)

    def mkdir(self, remote_dir):
        resp = self.session.request(method="MKCOL",
                                    url=self._url_join(remote_dir),
                                    auth=(self.user, self.password)
                                    )
        print(resp.ok, resp.content)

    def cp(self, source_remote_file, target_remote_dir=None, target_remote_file=None, overwrite=False):
        assert target_remote_dir is not None or target_remote_file is not None
        if not target_remote_file:
            file_name = os.path.basename(source_remote_file)
            target_remote_file = self._url_join(target_remote_dir, file_name)

        print(self._url_join(source_remote_file), self._url_join(target_remote_dir))
        resp = self.session.request(method="COPY",
                                    url=self._url_join(source_remote_file),
                                    auth=(self.user, self.password),
                                    headers={
                                        "Accept": "*/*",
                                        "Destination": target_remote_file,
                                        "Overwrite": f'{"T" if overwrite else "F"}'
                                    })

        print(resp.ok, resp.content)

    def mv(self, source_remote_file, target_remote_dir=None, target_remote_file=None, overwrite=False):
        assert target_remote_dir is not None or target_remote_file is not None
        if not target_remote_file:
            file_name = os.path.basename(source_remote_file)
            target_remote_file = self._url_join(target_remote_dir, file_name)

        print(self._url_join(source_remote_file), self._url_join(target_remote_dir))
        resp = self.session.request(method="MOVE",
                                    url=self._url_join(source_remote_file),
                                    auth=(self.user, self.password),
                                    headers = {
                                        "Accept": "*/*",
                                        "Destination": target_remote_file,
                                        "Overwrite": f'{"T" if overwrite else "F"}'
                                    })
        print(resp.ok, resp.content)

    def rm(self, remote_file):
        resp = self.session.request(method="DELETE",
                                    url=self._url_join(remote_file),
                                    auth=(self.user, self.password)
                                    )
        print(resp.ok, resp.content)

    def fetch_header(self, remote_file):
        resp = self.session.request(method="HEAD",
                                    url=self._url_join(remote_file),
                                    auth=(self.user, self.password)
                                    )

        print(resp.ok, resp.content, json.dumps(dict(resp.headers), indent=4))

    def publish(self):
        resp = self.session.request(method="PROPPATCH",
                                    url=self._url_join(remote_dir),
                                    auth=(self.user, self.password)
                                    )

if __name__ == "__main__":
    mywebdav = MyWebDav("https://dav.box.com/dav/", "xmings@163.com", "1234.com")
    # mywebdav.upload("test", open("d:\\abc.png", "rb"))
    mywebdav.fetch_header("abc.docx")
