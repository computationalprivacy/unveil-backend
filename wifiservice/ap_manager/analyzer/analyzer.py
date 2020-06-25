"""Analyze files for data.

{
    "Device_Info": {
        "MAC Address": "c0:ee:fb:f0:96:9a",
        "Manufacturer": "Oneplus Technologies",
        "Model Number": "A3003",
        "Build Details": "OPR6.170623.013",
        "OS Version": "Android 8.0.0"
    },
    "Apps": [
        ["WhatsApp","sensitive"],
        ["Facebook","not sensitive"],
        ["Facebook Messenger","not sensitive"],
        ["Amazon Shopping","sensitive"],
        ["Amazon Music", "not sensitive"],
        ["Snapchat","sensitive"],
        ["Reuters","sensitive"],
        ["Outlook Mobile", "not sensitive"],
        ["Skype", "not sensitive"],
        ["XE.com","sensitive"],
        ["HTTPS Everywhere", "not sensitive"],
        ["Gmail", "not sensitive"]
    ],
    "DNS_Queries": [
        ["www.linkedin.com","sensitive"],
        ["api.amazon.co.uk","not sensitive"],
        ["www.amazon.com","not sensitive"],
        ["apiservice.reuters.com","sensitive"]
    ],
    "Internet_Traffic": [
        [
            "11:43:38",
            "mqtt-mini.facebook.com",
            "HTTPS",
            "13kb"
        ],
        [
            "11:43:40",
            "www.facebook.com",
            "HTTPS",
            "3kb"
        ],
        [
            "11:43:40",
            "mtalk.google.com",
            "HTTPS",
            "4kb"
        ]
    ]
}
"""
import scapy.all as scapyall
from datetime import datetime
from probe_manager.analyzer.analyzer import get_oui
import re
import user_agents
import traceback
import urllib
import humanfriendly
from utils.dns_sensitivity import is_dns_sensitive
from utils.utils import get_hashed_mac


NOT_AVAILABLE = 'Not available'


class AccessPointDataAnalyzer(object):
    """Analyze data collected by an access point."""

    def __init__(self):
        """Initialize analyzer."""
        self.ap_ips = [
            '192.168.1.1',
            '192.168.1.255'
        ]

    def get_all_ips(self, packets):
        """Return list of all unique scapyall.IPs in the packets."""
        ip = {}
        for packet in packets:
            if packet.haslayer(scapyall.IP):
                src_ip = packet[scapyall.IP].src
                dst_ip = packet[scapyall.IP].dst
                ip[src_ip] = 1
                ip[dst_ip] = 1
        return list(ip.keys())

    def get_device_ips(self, all_ips):
        """Return a list of device scapyall.IPs."""
        device_ips = []
        for ip in all_ips:
            if ip.startswith('192.168') and ip not in self.ap_ips:
                device_ips.append(ip)
        return device_ips

    def get_data_http(self, pkt):
        """Get data from http packet."""
        payload = bytes(pkt[scapyall.TCP].payload)
        if len(payload) == 0:
            return None
        try:
            payload.decode("utf8")
        except Exception:
            print(payload)
            return None
        url_path = payload.decode("utf8").split(' ')[1]
        http_header_raw = payload[:payload.index(b"\r\n\r\n") + 2]
        http_header_parsed = dict(
            re.findall(
                r"(?P<name>.*?): (?P<value>.*?)\r\n",
                http_header_raw.decode("utf8")))
        url = urllib.parse.urljoin(
            'http://' + http_header_parsed.get('Host', ''), url_path)
        try:
            user_agent_str = http_header_parsed.get('User-Agent', '')
            ua = user_agents.parse(user_agent_str)
            os = ' '.join([ua.os.family, ua.os.version_string])
            return dict(
                model_num=ua.device.model,
                os=os,
                user_agent=user_agent_str,
                url=url)
        except Exception:
            traceback.print_exc()
            return dict(url=url)

    def get_relevant_ip_mac(self, pkt, ip_list):
        """Return relevant IP (one also in ip_list) and corresponding mac."""
        ip = None
        mac = None
        if pkt[scapyall.IP].src in ip_list:
            ip = pkt[scapyall.IP].src
            mac = pkt[scapyall.Ether].src
        elif pkt[scapyall.IP].dst in ip_list:
            ip = pkt[scapyall.IP].dst
            mac = pkt[scapyall.Ether].dst
        return ip, mac

    def get_device_info(self, ip_list, packets):
        """Get device info for the ip."""
        http_time2url = {}
        device_mac = {}
        device_details = {ip: {} for ip in ip_list}
        for pkt in packets:
            if pkt.haslayer(scapyall.IP):
                ip, mac = self.get_relevant_ip_mac(pkt, ip_list)
                if not(ip and mac):
                    continue
                device_mac[ip] = mac
                if (pkt.haslayer(scapyall.TCP) and
                        pkt[scapyall.TCP].dport == 80):
                    try:
                        dev_det = self.get_data_http(pkt)
                    except Exception:
                        print("=====Error in HTTP=====")
                        traceback.print_exc()
                        dev_det = None
                    if dev_det:
                        http_time2url[pkt.time] = dev_det['url']
                        dev_det.pop('url')
                        if len(dev_det['user_agent']) == 0:
                            continue
                        device_details[ip].update(dev_det)
        for ip, mac in device_mac.items():
            device_manufacturer = get_oui(mac)
            device_details[ip]['man'] = device_manufacturer
            device_details[ip]['mac'] = get_hashed_mac(mac)
        # print(device_details)
        return device_details, http_time2url

    def get_dns_queries(self, ip_list, packets):
        """Return mapping of ip to DNS queries."""
        dev2ip2dns_map = {ip: {} for ip in ip_list}
        for packet in packets:
            # We're only interested packets with a DNS Round Robin layer
            if not (packet.haslayer(scapyall.DNSRR) and
                    packet.haslayer(scapyall.IP)):
                continue
            # If the an(swer) is a DNSRR, print the name it replied with.
            if isinstance(packet.an, scapyall.DNSRR):
                dst_ip = packet[scapyall.IP].dst
                src_ip = packet[scapyall.IP].src
                if not(src_ip in ip_list or dst_ip in ip_list):
                    continue
                dev_ip = src_ip if src_ip in ip_list else dst_ip
                a_count = packet[scapyall.DNS].ancount
                dns_layers = a_count + 4
                try:
                    dns = packet[5].rrname.decode('utf-8')[:-1]
                except Exception:
                    continue
                i = 4
                while i < dns_layers:
                    i += 1
                    try:
                        # check for CNAME, NSEC, OPT DNS records
                        type_pkt = getattr(
                            packet[i], 'type', None)
                        if not type_pkt or type_pkt in (5, 41, 47):
                            continue
                        try:
                            ip = packet[i].rdata
                            if isinstance(packet[i].rdata, bytes):
                                ip = packet[i].rdata.decode('utf-8')
                            dev2ip2dns_map[dev_ip][ip] = dns
                        except Exception:
                            print("Exception found for packet.")
                            print(packet[i].show())
                            traceback.print_exc()
                    except Exception:
                        break
        return dev2ip2dns_map

    def get_ip2dns_list(self, ip_list, packets):
        """Return device to dns_queries list."""
        dev2ip2dns_map = self.get_dns_queries(ip_list, packets)
        global_ip2dns_map = {}
        dev2dns = {}
        for dev, ip2dns_map in dev2ip2dns_map.items():
            dev2dns[dev] = list(set([val for key, val in ip2dns_map.items()]))
            global_ip2dns_map.update(ip2dns_map)
        return dev2dns, global_ip2dns_map

    def get_internet_traffic(
            self, packets, ip_list, ip2dns_map, http_time2url):
        """Return Internet Traffic of the user."""
        sessions = packets.sessions()
        ip2sessions = {ip: {} for ip in ip_list}
        for k, v in sessions.items():
            session_details = k.split(' ')
            if session_details[0] == 'TCP':
                src_ip, src_port = session_details[1].split(':')
                dst_ip, dst_port = session_details[3].split(':')
                dev_ip, dev_port, site_ip, site_port = (
                    src_ip, src_port, dst_ip, dst_port) \
                    if src_ip in ip_list else (
                        dst_ip, dst_port, src_ip, src_port)
                if dev_ip not in ip_list or site_ip not in ip2dns_map:
                    continue
                protocol = 'HTTP' if site_port == '80' else 'HTTPS'
                if site_port not in ('443', '80'):
                    protocol = site_port
                url = ip2dns_map[site_ip]
                size = 0
                start_time = None
                try:
                    start_time = datetime.fromtimestamp(int(v[0].time))
                except Exception:
                    start_time = datetime.fromtimestamp(int(v[0].time) / 1000)
                for pkt in v:
                    if site_port == '80' and pkt.time in http_time2url:
                        url = http_time2url[pkt.time]
                    if pkt.haslayer(scapyall.Raw):
                        size += len(pkt[scapyall.Raw].load)
                if size == 0:
                    continue
                session_id = (dev_port, site_ip, site_port)
                if session_id not in ip2sessions[dev_ip]:
                    ip2sessions[dev_ip][session_id] = dict(
                        url='',
                        size=0,
                        start_time=datetime.now(),
                        protocol='')
                if len(url) > len(ip2sessions[dev_ip][session_id]['url']):
                    ip2sessions[dev_ip][session_id]['url'] = url
                ip2sessions[dev_ip][session_id]['size'] += size
                if start_time < ip2sessions[dev_ip][session_id]['start_time']:
                    ip2sessions[dev_ip][session_id]['start_time'] = start_time
                ip2sessions[dev_ip][session_id]['protocol'] = protocol
        return ip2sessions

    def __call__(self, datapath):
        """Run analytics over the packets."""
        packets = scapyall.rdpcap(datapath)
        all_ips = self.get_all_ips(packets)
        device_ips = self.get_device_ips(all_ips)
        device_details, http_time2url = self.get_device_info(
            device_ips, packets)
        device_dns, ip2dns_map = self.get_ip2dns_list(device_ips, packets)
        device_sessions = self.get_internet_traffic(
            packets, device_ips, ip2dns_map, http_time2url)
        return self.create_analysis_result(
            device_details, device_dns, device_sessions)

    def create_analysis_result(
            self, device_details, device_dns, device_sessions):
        """Create analysis results."""
        result = []
        for ip, dev_det in device_details.items():
            traffic = sorted(
                [
                    [
                        session['start_time'].time().isoformat(
                            timespec='seconds'),
                        session['url'], session['protocol'],
                        humanfriendly.format_size(session['size'])
                    ] for session_id, session in device_sessions[ip].items()
                ], key=lambda x: x[0])
            dev = {
                'Device_Info': {
                    "MAC Address": dev_det.get('mac', NOT_AVAILABLE),
                    "Manufacturer": dev_det.get('man', NOT_AVAILABLE),
                    "Model Number": dev_det.get('model_num', NOT_AVAILABLE),
                    "User-Agent": dev_det.get('user_agent', NOT_AVAILABLE),
                    "OS Version": dev_det.get('os', NOT_AVAILABLE)
                },
                'DNS_Queries': self.sanitize_dns(
                    [[k, "not sensitive"] for k in device_dns[ip]]),
                'Internet_Traffic': traffic
            }
            result.append(dev)
        return result

    def sanitize_dns(self, dns_list):
        """Return sanitized list of dns."""
        sanitized_list = []
        for dns in dns_list:
            if is_dns_sensitive(dns[0]):
                sanitized_list.insert(0, dns)
            else:
                sanitized_list.append(dns)
        return sanitized_list
