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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self):
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
        data =None
        try:
            data = json.loads(self.request.body)
            assert type(data.get("username")) == str # uni bi
            assert type(data.get("password")) == str # low_latency
            assert type(data.get("company_name")) == str
            # assert type(data.get("location")) == str # location
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self,name):
        result = await self.service.get_service_by_name(name)
        if result:
            self.write(json.dumps(result))
        else:
            self.set_status(404)
    async def delete(self,name):
        try:
            result = await self.service.delete_service(name)
            self.set_status(204)
        except Exception as e:
            self.write(json.dumps({"error":e}))
            self.set_status(400)

class LatencyHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self):
        try:
            result =await self.service.get_latency()
            self.write(json.dumps(result))
        except Exception as e:
            self.write(json.dumps({"error":e}))
            self.set_status(400)


def config_reader():
    with open("config.yaml") as file:
        config = yaml.load(file.read())
        # print(result)
        return config


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    application = tornado.web.Application([
        (r"/api/v1/vpn", VpnHandler),
        (r"/api/v1/vpn/(.[a-zA-Z0-9]+)", VpnDetailHandler),
        (r"/api/v1/latency", LatencyHandler)

    ])
    cfg = config_reader()

    http_server = HTTPServer(application)
    http_server.bind(9888)
    http_server.start(0)
    tornado.ioloop.IOLoop.current().start()

    # loop = asyncio.get_event_loop()
    # loop.run_forever()

    # tornado.ioloop.IOLoop.current().start()



