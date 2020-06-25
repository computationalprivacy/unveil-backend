"""Probe Analysis tester."""
from probe_manager.analyzer import ProbeAnalyzer


def run():
    """Run the test."""
    panalyzer = ProbeAnalyzer()
    print(panalyzer('07112018153734probereq.pcapng'))
