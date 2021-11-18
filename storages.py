import os

import aiofiles
import aiofiles.os


class FileStorage:
    def __init__(self, path=None):
        self.path = path
        if self.path is None:
            self.path = '/tmp/python-lfs-server'

    def get_path(self, repo, oid, mkdir):
        path = os.path.join(self.path, oid)
        dirname = os.path.dirname(path)
        if mkdir and (not os.path.exists(dirname)):
            os.mkdir(dirname)
        return path

    async def exists(self, request, repo, object):
        return os.path.exists(self.get_path(repo, object.oid, False))

    async def read(self, repo, oid):
        return aiofiles.open(self.get_path(repo, oid, False), mode='rb')

    async def save(self, repo, oid, data):
        async with aiofiles.open(self.get_path(repo, oid, True), mode='wb') as f:
            async for chunk in data:
                await f.write(chunk)
