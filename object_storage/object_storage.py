import requests
import json
import sys
import time
import os
import mimetypes
import base64

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.core.files.base import File
 
class ObjectStorageFile(File):
    def __init__(self, name, object_storage):
        self._name = name
        self.object_storage = object_storage
        self.file = StringIO()
        self._is_dirty = False

    def read(self):
        data = self.object_storage.retrieve_object(self._name)
        self.file = StringIO(data)
        return self.file.getvalue()

    def write(self, content, mimetype):
        #self.file = StringIO(content)
        #in_file = open(content, 'rU')
        #self.buffer = in_file.read()
        self.content = content
        self.mimetype = mimetype
        self._is_dirty = True

    def close(self):
        #if self._is_dirty:
        ret = self.object_storage.put_file(self._name, self.content, self.mimetype)
        self.file.close()
        return ret



class ObjectStorage(object): #ereditare da FILE
    HOST_AUTH = 'http://cloud.lab.fi-ware.org:4730'
    HOST_CDMI = 'http://130.206.82.9:8080'
    token_host = HOST_AUTH + "/v2.0/tokens"
    tenant_host = HOST_AUTH + "/v2.0/tenants"
    auth_reponse = None
    token = None
    auth = None
    auth_url = None
    username = None
    password = None

    def __init__(self):
        pass
        
    def authentication_request(self, username, password):
        '''
        Request authentication of user
        '''     
        # retrieve initial token
        self.username = username
        self.password = password

        headers = {'Content-Type': 'application/json'}
        body = '{"auth": {"passwordCredentials":{"username": "' + self.username + '", "password": "' + self.password + '"}}}'
        r = requests.post(self.token_host, data = body, headers = headers)
        datajson = r.json()

        initialtoken = datajson['access']['token']['id']
     
        # retrieve tenant
        headers = {'x-auth-token': initialtoken}
        r = requests.get(self.tenant_host, headers = headers)

        datajson = r.json()
        tenant = datajson['tenants'][0]['id']
  
     
        # retrieve authentication json
        headers = {'Content-Type': 'application/json'}
        body = '{"auth": {"tenantName": "'+tenant+'", "passwordCredentials":{"username": "'+username+'", "password": "'+password+'"}}}'
        r = requests.post(self.token_host, data = body, headers = headers)
        self.auth_reponse = r.json()
        return self.auth_reponse

    def get_token_auth(self):

        self.token = self.auth_reponse['access']['token']['id']
        for i in self.auth_reponse['access']['serviceCatalog']:
            if i['name'] == 'swift':
                self.auth_url = i['endpoints'][0]['publicURL']
                break
        self.auth = self.auth_url[self.auth_url.find("AUTH_"):]

        return 0
     
     
    def cdmi_request(self, verb, resource, headers, body):
        '''
        Do a HTTP request defined by HTTP verb, a Url, a dict of headers and a body.
        '''
        
        if body == None:
        	req = requests.request(method = verb, url = self.HOST_CDMI + "/cdmi/" + resource, headers = headers)
    	else:
        	req = requests.request(method = verb, url = self.HOST_CDMI + "/cdmi/" + resource, data = json.dumps(body), headers = headers)

        if req.status_code != requests.codes.ok:
        	return req

        body = req.text
        try:
            body_obj = json.loads(body)
        except ValueError:
            body_obj = body

        return body_obj
     
     
    def check_capabilities(self):
        headers = {"X-Auth-Token": self.token,
                   "Accept": "application/cdmi-capability",
                   "X-CDMI-Specification-Version": "1.0.1"}

        url = self.auth + "/cdmi_capabilities/"
     
        capabilities = self.cdmi_request('GET', url, headers, body = None)
        
        return capabilities
     
     
    def create_container(self, name):
        headers = {"X-Auth-Token": self.token,
                   "Content-Type": "application/cdmi-container",
                   "Accept": "application/cdmi-container",
                   "X-CDMI-Specification-Version": "1.0.1"}
        
        url = self.auth + "/" + name

        response = self.cdmi_request('PUT', url, headers, body = None)
        return response
     
     
    def list_container(self, name):
        headers = {"X-Auth-Token": self.token,
                   "Content-Type": "application/cdmi-container",
                   "Accept": "*/*",
                   "X-CDMI-Specification-Version": "1.0.1"}
        body = None
        if name is None:
            url = self.auth + "/"
        else:
            url = self.auth + "/" + name + "/"
        response = self.cdmi_request('GET', url, headers, body)
        if response is not None:
            return response['children']
        return None
     
    def store_object(self, object_name): #container_name, object_path
    
        container_name = ""
        url = self.auth + "/" + container_name + "/" + object_name
        guessed_type = mimetypes.guess_type(object_path, strict = True)
        mimetype = guessed_type[0]
        headers = 	{
        			"X-Auth-Token": self.token,
                   	"Content-Type": "application/cdmi-object",
                   	"X-CDMI-Specification-Version": "1.0.1",
                   	}
        print (mimetype)

        f = open(object_path, 'r')
        r = f.read()
        fileToSend = base64.b64encode(r)
        body = {"mimetype": mimetype, "valuetransferencoding": "base64", "value": fileToSend}
        
        return self.cdmi_request('PUT', url, headers, body)

    def put_file(self, object_name, content, mimetype, container_name = None):
        container_name = "1p"
        url = self.auth + '/' + container_name + '/' + object_name

        headers =   {
                    "X-Auth-Token": self.token,
                    "Content-Type": "application/cdmi-object",
                    "X-CDMI-Specification-Version": "1.0.1",
                    }

        fileToSend = base64.b64encode(content)
        body = {"mimetype": mimetype, "valuetransferencoding": "base64", "value": fileToSend}
        
        return self.cdmi_request('PUT', url, headers, body)

     
    def retrieve_object(self, object_name): #container_name, dest_folder_path, file_name
        headers = {"X-Auth-Token": self.token,
                   "Content-Type": "application/cdmi-object",
                   "Accept": "*/*",
                   "X-CDMI-Specification-Version": "1.0.1"}

        container_name = ""

        url = self.auth + "/" + container_name + "/" + object_name
     
    	resp = self.cdmi_request('GET', url, headers, body = None)

    	decoded = base64.b64decode(resp['value'], altchars = None)

    	ext = mimetypes.guess_extension(resp['mimetype'], strict=True)

        return decoded
     
     
    def delete_object(self, container_name, object_name):
        headers = {"X-Auth-Token": self.token,
                   "Content-Type": "application/cdmi-object",
                   "X-CDMI-Specification-Version": "1.0.1"}
        body = None
        url = self.auth + "/" + container_name + "/" + object_name
     
        return self.cdmi_request('DELETE', url, headers, body)
     
     
    def delete_container(self, container_name):
        headers = {"X-Auth-Token": self.token,
                   "Content-Type": "application/cdmi-container",
                   "X-CDMI-Specification-Version": "1.0.1"}
        body = None
        url = self.auth + "/" + container_name
     
        return self.cdmi_request('DELETE', url, headers, body)