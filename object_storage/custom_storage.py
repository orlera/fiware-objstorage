from django.conf import settings
from django.core.files.storage import Storage
from object_storage import ObjectStorage, ObjectStorageFile


class CustomStorage(Storage):
    def __init__(self):
        object_storage = ObjectStorage()
        object_storage.authentication_request(settings.USERNAME, settings.PASSWORD)
        object_storage.get_token_auth()
        self.object_storage = object_storage

    def _open(self, name, mode='rb'):
    	return ObjectStorageFile(name, self.object_storage)

    def _save(self, name, content, mimetype):
        object_storage_file = ObjectStorageFile(name, self.object_storage)
        object_storage_file.write(content, mimetype)
        ret = object_storage_file.close()
        return ret

    def exists(self, name):
        return False
        pass