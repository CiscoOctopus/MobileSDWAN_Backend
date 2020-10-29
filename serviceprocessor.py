import aioping

from nsoapiwrapper import NSOApiWrapper


class ServiceProcessor(object):
    """
    Backend connect to NSO Service
    """

    def __init__(self,config):
        self.address=config["nso"]["address"]
        self.port = config["nso"]["port"]
        self.username = config["nso"]["username"]
        self.password = config["nso"]["password"]
        self.nso = NSOApiWrapper(self.address,self.port,self.username,self.password)
        self.device_list=list(config["devices"].keys())
        self.device_ip = list(config["devices"].values())
        self.mapping={
            "apple":3092,
            "ibm":3093
        }

    async def create_service(self,username,company_name,password):
        """
        Create new vpn service
        :param username: vpn username
        :param company_name: vpn company name
        :param password: vpn password
        :return: true if success
        """

        if not self.mapping.get(company_name):
            raise Exception("Invalid company name")

        payload={
            "username": username,
            "company_name": company_name,
            "password": password,
            "vpn_group_id": self.mapping.get(company_name),
            "device": [{"name":i} for i in self.device_list]
        }
        wrapper = {"asauser:asauser": [payload]}
        await self.nso.post("restconf/data/tailf-ncs:services/",wrapper)
        return True

    async def get_service(self):
        """
        Get VPN Service info
        :return: Vpn info dict
        """
        data = await self.nso.get("restconf/data/tailf-ncs:services/asauser:asauser")
        current_service = []
        if data:
            for service in data["asauser:asauser"]:
                current_service.append({
                    "username":service["username"],
                    "company_name":service["company_name"],
                    "devices":[i["name"] for i in service["device"]]
                })
        sorted_data = sorted(current_service,key=lambda k:k["company_name"])
        return sorted_data


    async def get_service_by_name(self,username):
        """
        Get VPN Service info
        :param username: usename
        :return: vpn info dict
        """
        data = await self.nso.get(f"restconf/data/tailf-ncs:services/asauser:asauser={username}")
        if data:
            for service in data["asauser:asauser"]:
                return {
                    "username":service["username"],
                    "company_name":service["company_name"],
                    "devices":[i["name"] for i in service["device"]]
                }
        return None

    async def delete_service(self,username):
        """
        Delete service
        :param username: vpn name
        :return: true
        """

        resp = await self.nso.delete(f"restconf/data/tailf-ncs:services/asauser:asauser={username}",{})
        return True

    async def get_latency(self):
        """
        Check vpn nodes latency
        :return: vpn nodes latency from test server
        """
        latency_info = {}
        for i in range(0,len(self.device_list)):
            try:
                delay = await aioping.ping(self.device_ip[i])
                delay2 = await aioping.ping(self.device_ip[i])
                delay3 = await aioping.ping(self.device_ip[i])
                latency_info[self.device_list[i]] = 1000*(delay+delay2+delay3)/3
            except Exception as e:
                latency_info[self.device_list[i]]=0
        return latency_info



