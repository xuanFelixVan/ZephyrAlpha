STATUS_ARBITRATED = 'ARBITRATED'
STATUS_PENDING = 'PENDING'
STATUS_RESOLVED = 'RESOLVED'

def compute_archive_target(filepath):
    return filepath

def execute_archive(source_dir, target_dir=None, dry_run=False):
    return {'archived': 0, 'skipped': 0, 'errors': []}

def scan_drafts(directory):
    return []
