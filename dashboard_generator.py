import requests
import urllib3
import argparse
import re
from gen_dash import CreateDashboard
urllib3.disable_warnings()


class NagiosInfo:
    def __init__(self, root: str, token: str):
        self.NAGIOS_ROOT: str = root
        self.NAGIOS_TOKEN: str = token

    def _nagios_query(self, method: str = "GET",
                      endpoint: str = "objectjson.cgi",
                      query: str = None) -> dict:
        '''general nagios query function'''
        url: str = f'{self.NAGIOS_ROOT}/nagios/cgi-bin/{endpoint}?query={query}' # noqa 501
        payload: dict = {}
        headers: dict = {
            'Authorization': f'Basic {self.NAGIOS_TOKEN}'
        }
        try:
            response: requests.Response = requests.request(method, url,
                                                           headers=headers,
                                                           data=payload,
                                                           verify=False)
        except Exception as e:
            return f'error occured: {str(e)}'

        return response.json()

    def hostgroups(self) -> list:
        '''Return hostgroups from Nagios'''
        _hostgroups: dict = self._nagios_query(method="GET",
                                               query="hostgrouplist")
        return _hostgroups.get('data').get('hostgrouplist')

    def status_for_hostgroup(self, hostgroup: str) -> dict:
        '''Retrieve simple status list.
        An extended call is available as well.'''
        hostgroup = hostgroup.replace(' ', '+')
        _groupresults: dict = self._nagios_query(method="GET",
                                                 endpoint="statusjson.cgi",
                                                 query=f"servicelist&hostgroup={hostgroup}&details=true") # noqa E501
        return _groupresults.get('data').get('servicelist')

    def status_for_host(self, host: str) -> dict:
        '''Retrieve simple status list.
        An extended call is available as well.'''
        _hostresults: dict = self._nagios_query(method="GET",
                                                endpoint="statusjson.cgi",
                                                query=f"servicelist&hostname={host}") # noqa E501
        return _hostresults.get('data').get('servicelist')


def generate_graphs(host=None, data=None):
    graphs = []
    for k in sorted(data.keys(), key=str.casefold):
        #print(k)
        if len(data[k].get('perf_data')) > 0:
            graph = {
                'title': k,
                'dataSource': 'PNP',
                'targets': []
            }

            #for perflabel in (data[k].get('perf_data')).split():
            for perflabel in (re.split('\ |,', data[k].get('perf_data'))):
                if perflabel:
                    graph['targets'].append(
                        {
                            'host': host,
                            'service': k,
                            'fill': 'fill',
                            'perflabel': (perflabel.split('=')[0]).replace("'","")
                        }
                    )
            graphs.append(graph)
    return graphs


def generate_dashboards(data: dict, destination_folder: str='pro'):
    try:
        for server in data.keys():
            # print(j[server])
            metrics = generate_graphs(host=server, data=data[server])
            #print(json.dumps(metrics, indent=4))
            dash_mgr = CreateDashboard(title=server)
            dashboard = dash_mgr.create(metrics)
            if dash_mgr.save_dashboard(f'{destination_folder}/{server}_dashboard.json', dashboard):
                print('done')
            else:
                print('something went wrong.')
    except AttributeError as e:
        print(f"Got error: {e}, guessing maybe your hostgroup doesn't exist.")
    

if __name__ == "__main__":
    NAGIOS_ROOT = ""
    NAGIOS_TOKEN = ""
    nagios_info = NagiosInfo(root=NAGIOS_ROOT, token=NAGIOS_TOKEN)

    parser = argparse.ArgumentParser()
    parser.add_argument("hostgroup", help="a nagios hostgroup, must exist")
    parser.add_argument("folder", help="folder where to save the dashboards")
    args = parser.parse_args()
    
    nagios_data = nagios_info.status_for_hostgroup(args.hostgroup.replace(' ','+'))
    generate_dashboards(nagios_data, args.folder)
