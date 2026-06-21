def detect_overlaps(blueprints=None, path=None):
    return []

class OverlapResult:
    def __init__(self, blueprint_a='', blueprint_b='', overlapping_fields=None):
        self.blueprint_a = blueprint_a
        self.blueprint_b = blueprint_b
        self.overlapping_fields = overlapping_fields or []

def extract_components(blueprint_path):
    return []

def run_validation(path=None):
    return []

def scan_draft_components(path):
    return []
