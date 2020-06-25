"""DNS Sensitivity check utils."""

common_apps_dns = [
    'whatsapp', 'linkedin', 'akamaiedge', 'skype', 'outlook',
    'microsoft', 'twitter', 'apple', 'amazon', 'instagram',
    'office365', 'google', 'doubleclick', 'facebook', 'pool.ntp',
    'appsflyer'
]


def is_dns_sensitive(dns):
    """Is DNS sensitive."""
    return not any([dns.find(k) != -1 for k in common_apps_dns])
