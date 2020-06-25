"""Analyses the packets to return json of SSIDs and phones captured."""
from scapy.all import rdpcap, Dot11ProbeReq
from netaddr.core import NotRegisteredError
from netaddr import EUI
from utils.optout import get_opted_out_mac
from .wigle import Wigle
from .wifispc import WifiSpc


def get_oui(mac):
    """Get OUI."""
    macf = None
    maco = EUI(mac)
    try:
        macf = maco.oui.registration().org
    except NotRegisteredError:
        macf = "Not available"
    return macf


def get_ssid_packet(packet):
    """Get SSID from packet."""
    ssid = None
    if packet.ID == 0:
        try:
            ssid = packet.info.decode('utf8')
        except Exception:
            ssid = None
    return ssid


def is_mac_global(mac_addr):
    """Return if mac address is global."""
    mac_addr = EUI(mac_addr)
    return mac_addr.bits()[6] == '0'  # 0 means globally administrated, unique


def get_mac_oui(mac_addr):
    """Return OUI for mac."""
    mac_addr = EUI(mac_addr)
    return mac_addr.bits()[:24]


def get_mac_from_packet(packet):
    """Return mac from the packet."""
    return packet.addr2


class ProbeAnalyzerHelper(object):
    """Convert SSID to addresses for visualisation.

    Attributes:
    ssid_names (dict): keys= ssid_name, value=number of users.
    phones (dict): key=company, value= number of users.
    ssid_results (list of dicts): resulting dictionaries according to
        ssid_names, without empty dicts, only valid results.

    """

    def __init__(self, ssid_collection):
        """Initialize analyzer."""
        self.ssid_collection = ssid_collection
        self.wifispc = WifiSpc(ssid_collection)
        self.wigle = Wigle()

    def check_in_collection(self, ssid):
        """Check if ssid occurs in collection."""
        ssid_datum = self.ssid_collection.find_one({'ssid': ssid})
        return ssid_datum

    def insert_in_collection(self, ssid_datum):
        """Insert in collection."""
        self.ssid_collection.replace_one(
            {'ssid': ssid_datum['ssid']}, ssid_datum, upsert=True)

    def __call__(self, data):
        """Return a visualisable version for data.

        Uses python files for each ssid name
        Returns:
        Precentage of SSID Found
        """
        ssid_data = data['ssid']
        ssid_address = []
        for ssid_name, users_number in ssid_data.items():
            ssid_datum = {'users': users_number}
            lookup = self.check_in_collection(ssid_name)
            insert_in_db = lookup is None
            if not lookup:
                try:
                    lookup = self.wifispc.lookup_ssid(ssid_name)
                except Exception:
                    print('problem in WIFI spc Lookup')
            if not lookup:
                try:
                    lookup = self.wigle.lookup_ssid(ssid_name)
                except Exception:
                    print('problem in Wigle Lookup')
            if lookup:
                if '_id' in lookup:
                    del lookup['_id']
                ssid_datum.update(lookup)
                ssid_address.append(ssid_datum)
                if insert_in_db:
                    self.insert_in_collection(lookup)
        if len(ssid_data.keys()) != 0:
            print("SSID fetch accuracy - {}".format(
                len(ssid_address) / len(ssid_data.keys())))
        return {
            'markers': ssid_address,
            'phones': data['phones']
        }


class ProbeAnalyzer(object):
    """Analyze probe requests and insert results in DB."""

    def __init__(self, ssid_collection):
        """Initialize analysers."""
        self.helper = ProbeAnalyzerHelper(ssid_collection)
        self.opted_out_mac = get_opted_out_mac()

    def _read_packets(self, trace_path):
        """Return PR packets."""
        packets = rdpcap(trace_path)
        pr_packets = []
        for packet in packets:
            if packet.haslayer(Dot11ProbeReq):  # is a probe request
                pr_packets.append(packet)
        return pr_packets

    def _get_mac2id(self, packets):
        """Return unique mac to id."""
        unique_macs = 0
        unique_devices = {}
        mac2id = {}
        for packet in packets:
            mac = get_mac_from_packet(packet)
            if mac:
                mac = mac.lower()
            elif (not mac or mac in self.opted_out_mac or mac in mac2id):
                continue
            mac_oui = get_mac_oui(mac)
            package_time = int(packet.time)
            mac_unique = False
            if is_mac_global(mac):
                mac_unique = True
            elif (mac_oui, package_time) not in unique_devices:
                unique_devices[(mac_oui, package_time)] = unique_macs
                mac_unique = True
            else:
                mac2id[mac] = unique_devices[(mac_oui, package_time)]
            if mac_unique:
                mac2id[mac] = unique_macs
                unique_macs += 1
        return unique_macs, mac2id

    def _get_man2num_phones(self, mac2id):
        """Return num of phones per manufacturer."""
        phones2oui = {}
        for mac, uid in mac2id.items():
            phones2oui[uid] = get_oui(mac)
        num_phones = {}
        for mac, mac_man in phones2oui.items():
            if mac_man not in num_phones:
                num_phones[mac_man] = 0
            num_phones[mac_man] += 1
        # print('num_phones', num_phones)
        return num_phones

    def _get_addr2ssid(self, mac2id, packets):
        """Return unique count per ssid."""
        addr2ssid_map = {}
        for packet in packets:
            mac = get_mac_from_packet(packet)
            uid = mac2id[mac]
            ssid = get_ssid_packet(packet)
            if not ssid:
                continue
            if (uid, ssid) not in addr2ssid_map:
                addr2ssid_map[(uid, ssid)] = 1
        # print('length (uid,ssid)', len(addr2ssid_map.keys()))
        num_phones_per_ssid = {}
        for addr_ssid_tup, val in addr2ssid_map.items():
            addr, ssid = addr_ssid_tup
            if ssid not in num_phones_per_ssid:
                num_phones_per_ssid[ssid] = 0
            num_phones_per_ssid[ssid] += 1
        return num_phones_per_ssid

    def __call__(self, trace_path):
        """Analyze the probe requests packet capture."""
        packets = self._read_packets(trace_path)
        unique_macs, mac2id = self._get_mac2id(packets)
        num_phones_per_ssid = self._get_addr2ssid(mac2id, packets)
        num_phones = self._get_man2num_phones(mac2id)
        del num_phones['Not available']
        data = {}
        data['ssid'] = num_phones_per_ssid
        data['phones'] = num_phones
        return self.helper(data)
