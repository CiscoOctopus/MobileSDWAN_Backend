import argparse
import asyncio
import getopt
import logging
import os
import sys
import traceback
from tornado.httpserver import HTTPServer

import tornado.ioloop
import tornado.web
import json

import yaml

from serviceprocessor import ServiceProcessor


class BaseHandler(tornado.web.RequestHandler):
    """
    Base Handler class to modify CORS header.

    """
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', ' GET, POST, PUT, DELETE, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', ','.join(
            self.request.headers.get('Access-Control-Request-Headers', '').split(',') +
            ['Content-Type']
        ))
        self.set_header('Content-Type', 'application/json')
        self.service = ServiceProcessor(cfg)


    def options(self, *args, **kwargs):
        # no body
        self.set_status(204)
        self.finish()

class VpnHandler(BaseHandler):
    """
    VPN Rest API Client to create VPN User/ Query VPN info

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self):
        """
        Query VPN Info
        :return: vpn info dict
        """
        try:
            result =await self.service.get_service()
            if result:
                self.write(json.dumps(result))
            else:
                self.set_status(500)
        except Exception as e:
            self.write(json.dumps({"error":e}))
            self.set_status(400)

    async def post(self):
        """
        Create new VPN
        :return: 204
        """
        data =None
        try:
            data = json.loads(self.request.body)
            assert type(data.get("username")) == str # Username
            assert type(data.get("password")) == str # Password
            assert type(data.get("company_name")) == str # Company name
        except Exception as e:
            self.set_status(400)
            self.write(json.dumps({"error": "Invalid Params"}))
        try:
            resp = await self.service.create_service(data.get("username"),data.get("company_name"),data.get("password"))
            self.set_status(204)
        except Exception as e:
            self.write(json.dumps({"error":e}))
            self.set_status(400)


class VpnDetailHandler(BaseHandler):
    '''
    Get VPN Detail infos
    Delete Specific VPN by name
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self,name):
        """
        Get VPN Info API
        :param name: vpn name
        :return: vpn info dict
        """
        result = await self.service.get_service_by_name(name)
        if result:
            self.write(json.dumps(result))
        else:
            self.set_status(404)
    async def delete(self,name):
        """
        Delete VPN API
        :param name: vpn name
        :return: 204 if deleted
        """
        try:
            result = await self.service.delete_service(name)
            self.set_status(204)
        except Exception as e:
            self.write(json.dumps({"error":e}))
            self.set_status(400)

class LatencyHandler(BaseHandler):
    """
    Deprecated latency api to calculate latency from *server* to *vpn_endpoint*, Used of alive checks
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self):
        """
        Get VPN latency infos
        :return: vpn latency info dict
        """
        try:
            result =await self.service.get_latency()
            self.write(json.dumps(result))
        except Exception as e:
            self.write(json.dumps({"error":e}))
            self.set_status(400)

class ServerHandler(BaseHandler):
    """
    Get Devices managed
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self):
        """
        Get managed ASA endpoints
        :return: asa server dict
        """
        try:
            self.write(json.dumps(cfg["devices"]))
        except Exception as e:
            self.write(json.dumps({"error":e}))
            self.set_status(400)


def config_reader():
    """
    Load config.yaml
    :return: config dict
    """
    with open("config.yaml") as file:
        config = yaml.load(file.read())
        # print(result)
        return config


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    # Create API endpoints
    application = tornado.web.Application([
        (r"/api/v1/vpn", VpnHandler),
        (r"/api/v1/vpn/(.[a-zA-Z0-9]+)", VpnDetailHandler),
        (r"/api/v1/latency", LatencyHandler),
        (r"/api/v1/server", ServerHandler),

    ])
    cfg = config_reader()

    http_server = HTTPServer(application)
    http_server.bind(9888)
    http_server.start(0)
    tornado.ioloop.IOLoop.current().start()


