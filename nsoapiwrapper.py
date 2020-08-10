import json

import aiohttp


class NSOApiWrapper(object):

    def __init__(self,address,port,username,password):
        self.address=address
        self.port = port
        self.username = username
        self.password = password

    def _build_url(self,path):
        return f"http://{self.address}:{self.port}/{path}"

    async def get(self,path):
        headers = {"Accept":"application/yang-data+json"}
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(self.username,self.password)) as session:
            async with session.get(self._build_url(path),headers=headers) as resp:
                if resp.status>=300:
                    raise Exception("Error : {}".format(resp.status))
                elif resp.status==200:
                    result = await resp.text()
                    return json.loads(result)


    async def post(self,path,data):
        headers = {"Accept":"application/yang-data+json","Content-Type":"application/yang-data+json"}
        auth =aiohttp.BasicAuth(self.username,self.password)
        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.post(self._build_url(path),json=data,headers=headers) as resp:
                if resp.status>=300:
                    raise Exception("Error : {}".format(resp.status))
                elif resp.status==200:
                    result = await resp.text()
                    return json.loads(result)



    async def delete(self,path,data):
        headers = {"Accept":"application/yang-data+json","Content-Type":"application/yang-data+json"}
        auth =aiohttp.BasicAuth(self.username,self.password)
        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.delete(self._build_url(path),json=data,headers=headers) as resp:
                if resp.status>=300:
                    raise Exception("Error : {}".format(resp.status))
                elif resp.status==200:
                    result = await resp.text()
                    return json.loads(result)
