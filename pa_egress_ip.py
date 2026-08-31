#!/usr/bin/env python

import requests
import json
import sys, os


here = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(here, ".."))
sys.path.insert(0, project_root)

import pa_env  # noqa

def verify_api(api_url)->bool:
	p_token= pa_env.X_PAN_KEY
	#exit(0)

	headers = {
	#    'Accept': 'application/json',
		'header-api-key':  p_token
	}
	params = {}
	#payload = json.dumps({'timespan': p_timespan , 'statuses': ["Online"]})

	payload = json.dumps({"serviceType": "gp_portal", "addrType": "all","location": "deployed"})
	#print(headers)
	try:
		r = requests.request("POST", api_url, headers=headers, data=payload)
		if r.status_code == 200:
			data = r.json()
			json_formatted_str = json.dumps(data, indent=2)
			#print(json_formatted_str)
			print("Enviroment Found - API Key OK")
			return True
		else:
			print("Incorrect Enviroment")
			return False
	except:
		print("Unable to contact Prisma cloud")
		return False


def get_ips(api_url, stype)->bool:
	p_token= pa_env.X_PAN_KEY
	headers = {
		'header-api-key':  p_token
	}
	params = {}
	payload = json.dumps({"serviceType": stype, "addrType": "all","location": "deployed"})
	try:
		r = requests.request("POST", api_url, headers=headers, data=payload)
		if r.status_code == 200:
			data = r.json()
			json_formatted_str = json.dumps(data, indent=2)
                        #print(json_formatted_str)
                        #print("URL and API Key OK")
		elif r.status_code == 400:
			data = r.json()
			print(data["result"])
			return False
		else:
			print("There is an issue connecting to the Meraki platform.  Please check the API Key")
			return False
	except:
		print("Unable to contact Meraki cloud")
		return False
	ip_list=[]
	zone_list=[]
	service_list=[]
	location_list=[]
	for record in data["result"]:
		for address in record["addresses"]:
			#print(address)
			ip_list.append(address)
			zone_list.append(record["zone"])
			service_list.append(stype)
			location_list.append("deployed")

	payload = json.dumps({"serviceType": stype, "addrType": "all","location": "all"})
	try:
		r = requests.request("POST", api_url, headers=headers, data=payload)
		if r.status_code == 200:
			data = r.json()
			json_formatted_str = json.dumps(data, indent=2)
			if stype == "remote_network":
				for record in data["result"]:
					for record2 in record["address_details"]:
						if record2["addressType"] == "service_ip":
							print(record2["node_name"])
                        #print("URL and API Key OK")
		else:
			print("There is an issue connecting to the Meraki platform.  Please check the API Key")
			return False
	except:
		print("Unable to contact Meraki cloud")
		return False
	for record in data["result"]:
		for address in record["addresses"]:
			try:
				idx = ip_list.index(address)
			except:
				ip_list.append(address)
				zone_list.append(record["zone"])
				service_list.append(stype)
				location_list.append("reserved")

	for idx, addr in enumerate(ip_list):
		print("Egress IP: " + addr + " , Zone: " + zone_list[idx] + " , Allocation: " + location_list[idx])

	#print(ip_list)
	#print(zone_list)
	#print(service_list)
	#print(location_list)





def main():
	env_list = ["lab","prod","prod2", "prod3", "prod4", "prod5", "prod6", "prod7"]
	correct_url = ""
	for env in env_list:
		print("Testing Enviroment: "+ env)
		url = "https://api." + env + ".datapath.prismaaccess.com/getPrismaAccessIP/v2"
		#print("trying URL: "+ url)
		if verify_api(url) == True:
			correct_url = url
			break
	if correct_url != "":
		#print(correct_url)
		print("\nFetching Mobile Users - GlobalProtect Gateway IP addresses")
		get_ips(correct_url,"gp_gateway")
		print("\nFetching Mobile Users - GlobalProtect Portal IP addresses")
		get_ips(correct_url,"gp_portal")
		print("\nFetching Remote Networks IP addresses")
		get_ips(correct_url,"remote_network")
		print("\nFetching  Explicit Proxy location, ACS Services, and the network load balancers IP addresses")
		get_ips(correct_url,"swg_proxy")


	else:
		print("no valid API")


if __name__ == '__main__':
	main()

