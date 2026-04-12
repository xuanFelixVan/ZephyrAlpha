---
module_id: 09_AUDIT_CONFIGURATION_SCHEDULED_AUDIT_CONFIGURATION
layer: layer_09
version: 1.0.0
status: Active
responsibility:
  - Scheduled Audit Configuration相关业务
standard_type: ﻠﻝﺛ؟ﮔﮒ
applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨ?
compliance_level: ﮔ۲ﮒﺙﮔﮒ
parent_document: DOCUMENT_GOVERNANCE_PROCESS_STANDARD.md
implementation_status: ﮒﺓﺎﮒ؟ﮔ?
owner: ﮔﮔ۰۲ﻝ؟۰ﻝﮒ?
created_date: 2026-04-02
last_updated: 2026-04-07
---

## 1. ﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻠﻝﺛ؟ﮔ۵ﻟ۶



### 1.1 ﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻝﺎﭨﮒ



| ﻛﭨﭨﮒ۰ﮒﻝ۶ﺍ | ﻠ۱ﻝ | ﮔ۶ﻟ۰ﮔﭘﻠﺑ | ﮒ؟۰ﻟ؟۰ﮒﮒ؟ﺗ | ﻟﺝﮒﭦﻛﺛﻝﺛ؟ |

|---------|------|----------|----------|---------|

| **ﮒﺟ،ﻠﮒ؟۰ﻟ؟?* | ﮔﺁﮒ۷ﻛﺕ | ﮒﮔ۷2:00 | ﻠﺝﮔ۴ﮔﮔﮔ۶ﻙﮒﮔﺍﮔ؟ﮒ؟ﮔﺑﮔ?| audit_reports/weekly/ |

| **ﮔﮒﮒ؟۰ﻟ؟۰** | ﮔﺁﮔ1ﮔ?| ﮒﮔ۷3:00 | ﮔﮔ۰۲ﮒﻝﺎﭨﻙﮒﺛﮒﻟ۶ﻟﻙﻝﺑ۱ﮒﺙﮒ؟ﮔﺑﮔ?| audit_reports/monthly/ |

| **ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰** | ﮔﺁﮒ۲ﮒﭦ۵ﻠ۵ﮔ?| ﮒﺓ۴ﻛﺛﮔﭘﻠﺑ | ﻛﺕﮒﺎﮒ؟۰ﻟ؟۰ﺅﺙL1-L3ﺅﺙﻙﻛﭦﮒ۳۶ﮒﮒﻝ؛۵ﮒﮔ?| audit_reports/quarterly/ |

| **ﻛﺕﻠ۰ﺗﮒ؟۰ﻟ؟۰** | ﻛﭦﻛﭨﭘﻟ۶۵ﮒ | ﮒﮔﺑﮒ?4ﮒﺍﮔﭘﮒ?| ﮒﮔﺑﮒﺛﺎﮒﻟﮒﺑﻙﮔﮔ۰۲ﻛﺕﻟﺑﮔ?| audit_reports/adhoc/ |



### 1.2 ﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻛﺙﮒﻝﭦ?



- **P0**: ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﺅﺙﮔﺁﮒ۷ﮔ۶ﻟ۰ﺅﺙﻝ۰؟ﻛﺟﮒﭦﮔ؛ﻟﺑ۷ﻠﺅﺙ

- **P1**: ﮔﮒﮒ؟۰ﻟ؟۰ﺅﺙﮔﺁﮔﮔ۶ﻟ۰ﺅﺙﻝ۰؟ﻛﺟﻟ۶ﻟﻝ؛۵ﮒﺅﺙ?

- **P2**: ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﺅﺙﮔﺁﮒ۲ﮒﭦ۵ﮔ۶ﻟ۰ﺅﺙﻝ۰؟ﻛﺟﻛﺕﻛﺕﮔﮒﺅﺙ

- **P3**: ﻛﺕﻠ۰ﺗﮒ؟۰ﻟ؟۰ﺅﺙﻛﭦﻛﭨﭘﻟ۶۵ﮒﺅﺙﻝ۰؟ﻛﺟﮒﮔﺑﻛﺕﻟﺑﮔ۶ﺅﺙ



---



## 2. Cronﻛﭨﭨﮒ۰ﻠﻝﺛ؟



### 2.1 Linux/Unixﻝﺏﭨﻝﭨ



**ﻝﺙﻟﺝcrontab**:

```bash

crontab -e

```



**ﮔﺓﭨﮒﻛﭨ۴ﻛﺕﻛﭨﭨﮒ۰**:



```bash

# ZephyrAlphaﮔﮔ۰۲ﮔﺎﭨﻝﮒ؟ﮔﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰



# ﮒﺟ،ﻠﮒ؟۰ﻟ؟?- ﮔﺁﮒ۷ﻛﺕﮒﮔ۷2:00ﮔ۶ﻟ۰

0 2 * * 1 cd /path/to/ZephyrAlpha && /usr/bin/python3 scripts/document_auditor.py --quick --output "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/weekly_$(date +\%Y\%m\%d).json" >> logs/audit.log 2>&1



# ﮔﮒﮒ؟۰ﻟ؟۰ - ﮔﺁﮔ1ﮔ۴ﮒﮔ?:00ﮔ۶ﻟ۰

0 3 1 * * cd /path/to/ZephyrAlpha && /usr/bin/python3 scripts/document_auditor.py --all --output "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/monthly_$(date +\%Y\%m\%d).json" >> logs/audit.log 2>&1



# ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ - ﮔﺁﮒ۲ﮒﭦ۵ﻠ۵ﮔ۴ﮒﮔ?:00ﮔ۶ﻟ۰ﺅﺙ?ﮔﻙ?ﮔﻙ?ﮔﻙ?0ﮔﺅﺙ

0 3 1 1,4,7,10 * cd /path/to/ZephyrAlpha && /usr/bin/python3 scripts/document_auditor.py --deep --output "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/quarterly_$(date +\%Y\%m\%d).json" >> logs/audit.log 2>&1



# ﮒﮔﺍﮔ؟ﮒ؟ﮔﺑﮔ۶ﮔ۲ﮔ?- ﮔﺁﮒ۷ﮔ۴ﮒﮔ?:30ﮔ۶ﻟ۰

30 2 * * 0 cd /path/to/ZephyrAlpha && /usr/bin/python3 scripts/metadata_enhancer.py --scan --output "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/metadata_$(date +\%Y\%m\%d).json" >> logs/audit.log 2>&1



# ﮔﮔ۰۲ﮒﻝﺎﭨﮔ۲ﮔ?- ﮔﺁﮔ15ﮔ۴ﮒﮔ?:00ﮔ۶ﻟ۰

0 3 15 * * cd /path/to/ZephyrAlpha && /usr/bin/python3 scripts/document_classifier.py --scan --output "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/classification_$(date +\%Y\%m\%d).json" >> logs/audit.log 2>&1

```



### 2.2 Windowsﻝﺏﭨﻝﭨﺅﺙﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦﺅﺙ



**ﮒﮒﭨﭦﻛﭨﭨﮒ۰ﻟ؟۰ﮒ**:



1. **ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ?*:

   - ﮒﻝ۶ﺍ: `ZephyrAlpha_Weekly_Audit`

   - ﻟ۶۵ﮒﮒ? ﮔﺁﮒ۷ﻛﺕﮒﮔ۷2:00

   - ﮔﻛﺛ: ﮒﺁﮒ۷ﻝ۷ﮒﭦ

   - ﻝ۷ﮒﭦ: `python`

   - ﮒﮔﺍ: `scripts\document_auditor.py --quick --output "docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\weekly_%date:~0,4%%date:~5,2%%date:~8,2%.json"`

   - ﻟﭖﺓﮒ۶ﻛﺛﻝﺛ؟: `D:\ZephyrAlpha`



2. **ﮔﮒﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰**:

   - ﮒﻝ۶ﺍ: `ZephyrAlpha_Monthly_Audit`

   - ﻟ۶۵ﮒﮒ? ﮔﺁﮔ1ﮔ۴ﮒﮔ?:00

   - ﮔﻛﺛ: ﮒﺁﮒ۷ﻝ۷ﮒﭦ

   - ﻝ۷ﮒﭦ: `python`

   - ﮒﮔﺍ: `scripts\document_auditor.py --all --output "docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\monthly_%date:~0,4%%date:~5,2%%date:~8,2%.json"`

   - ﻟﭖﺓﮒ۶ﻛﺛﻝﺛ؟: `D:\ZephyrAlpha`



3. **ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰**:

   - ﮒﻝ۶ﺍ: `ZephyrAlpha_Quarterly_Audit`

- ﻟ۶۵ﮒﮒ? ﮔﺁﮒ۲ﮒﭦ۵ﻠ۵ﮔ۴ﮒﮔ?:00ﺅﺙﮔﮒ۷ﻟ؟ﺝﻝﺛ؟ﺅﺙ

   - ﮔﻛﺛ: ﮒﺁﮒ۷ﻝ۷ﮒﭦ

   - ﻝ۷ﮒﭦ: `python`

   - ﮒﮔﺍ: `scripts\document_auditor.py --deep --output "docs\05_IMPLEMENTATION\07_OPERATIONS\audit_state\quarterly_%date:~0,4%%date:~5,2%%date:~8,2%.json"`

   - ﻟﭖﺓﮒ۶ﻛﺛﻝﺛ؟: `D:\ZephyrAlpha`



---



## 3. ﮒ؟۰ﻟ؟۰ﻟﮔ؛ﻠﻝﺛ؟



### 3.1 ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﻟﮔ?



**ﮔﻛﭨﭘ**: `scripts/scheduled_quick_audit.py`



```python

#!/usr/bin/env python3

"""

ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﻟﮔ?

ﮒﻟﺛ: ﮔﺁﮒ۷ﮔ۶ﻟ۰ﺅﺙﮔ۲ﮔ۴ﻠﺝﮔ۴ﮔﮔﮔ۶ﮒﮒﮔﺍﮔ؟ﮒ؟ﮔﺑﮔ?

"""



import os

import sys

import json

import logging

from datetime import datetime

from pathlib import Path



# ﮔﺓﭨﮒﻠ۰ﺗﻝ؟ﮔﺗﻝ؟ﮒﺛﮒﺍﻟﺓﺁﮒﺝ

sys.path.insert(0, str(Path(__file__).parent.parent))



from scripts.document_auditor import DocumentAuditor



# ﻠﻝﺛ؟ﮔ۴ﮒﺟ

logging.basicConfig(

    level=logging.INFO,

    format='%(asctime)s - %(levelname)s - %(message)s',

    handlers=[

        logging.FileHandler('logs/quick_audit.log'),

        logging.StreamHandler()

    ]

)



logger = logging.getLogger(__name__)



def run_quick_audit():

    """ﮔ۶ﻟ۰ﮒﺟ،ﻠﮒ؟۰ﻟ؟?""

    try:

        logger.info("ﮒﺙﮒ۶ﮒﺟ،ﻠﮒ؟۰ﻟ؟?..")

        

        # ﮒﮒ۶ﮒﮒ؟۰ﻟ؟۰ﮒ۷

        auditor = DocumentAuditor(project_root='.')

        

        # ﮔ۶ﻟ۰ﮒﺟ،ﻠﮒ؟۰ﻟ؟?

        results = auditor.quick_audit()

        

        # ﻝﮔﮔ۴ﮒﮔﻛﭨﭘﮒ?

        timestamp = datetime.now().strftime('%Y%m%d')

        output_file = f'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/weekly_{timestamp}.json'

        

# ﻛﺟﮒﮔ۴ﮒ

        with open(output_file, 'w', encoding='utf-8') as f:

            json.dump(results, f, indent=2, ensure_ascii=False)

        

logger.info(f"ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮒ؟ﮔﺅﺙﮔ۴ﮒﮒﺓﺎﻛﺟﮒﮒﺍ: {output_file}")

        

        # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮔﻛﺕ۴ﻠﻠ؟ﻠ۱

        if results['summary']['total_issues'] > 0:

            logger.warning(f"ﮒﻝﺍ {results['summary']['total_issues']} ﻛﺕ۹ﻠ؟ﻠ۱?)

            

            # ﮒﻠﻠﻝ۴ﺅﺙﮒﺁﻠﺅﺙ

            send_notification(results)

        

        return 0

        

    except Exception as e:

        logger.error(f"ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮒ۳ﺎﻟﺑ? {str(e)}")

        return 1



def send_notification(results):

    """ﮒﻠﮒ؟۰ﻟ؟۰ﻠﻝ۴ﺅﺙﮒﺁﻠﺅﺙ"""

# ﻟﺟﻠﮒﺁﻛﭨ۴ﻠﮔﻠ؟ﻛﭨﭘﻙﻠﻠﻙﻛﺙﻛﺕﮒﺝ؟ﻛﺟ۰ﻝﻠﻝ۴ﮔﺗﮒﺙ

    # ﻝ۳ﭦﻛﺝﺅﺙﮒﻠﻠ؟ﻛﭨﭘﻠﻝ۴

    pass



if __name__ == '__main__':

    sys.exit(run_quick_audit())

```



### 3.2 ﮔﮒﮒ؟۰ﻟ؟۰ﻟﮔ؛



**ﮔﻛﭨﭘ**: `scripts/scheduled_standard_audit.py`



```python

#!/usr/bin/env python3

"""

ﮔﮒﮒ؟۰ﻟ؟۰ﻟﮔ؛

ﮒﻟﺛ: ﮔﺁﮔﮔ۶ﻟ۰ﺅﺙﮔ۲ﮔ۴ﮔﮔ۰۲ﮒﻝﺎﭨﻙﮒﺛﮒﻟ۶ﻟﻙﻝﺑ۱ﮒﺙﮒ؟ﮔﺑﮔ?

"""



import os

import sys

import json

import logging

from datetime import datetime

from pathlib import Path



sys.path.insert(0, str(Path(__file__).parent.parent))



from scripts.document_auditor import DocumentAuditor



logging.basicConfig(

    level=logging.INFO,

    format='%(asctime)s - %(levelname)s - %(message)s',

    handlers=[

        logging.FileHandler('logs/standard_audit.log'),

        logging.StreamHandler()

    ]

)



logger = logging.getLogger(__name__)



def run_standard_audit():

"""ﮔ۶ﻟ۰ﮔﮒﮒ؟۰ﻟ؟۰"""

    try:

logger.info("ﮒﺙﮒ۶ﮔﮒﮒ؟۰ﻟ؟?..")

        

        auditor = DocumentAuditor(project_root='.')

        results = auditor.full_audit()

        

        timestamp = datetime.now().strftime('%Y%m%d')

        output_file = f'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/monthly_{timestamp}.json'

        

        with open(output_file, 'w', encoding='utf-8') as f:

            json.dump(results, f, indent=2, ensure_ascii=False)

        

logger.info(f"ﮔﮒﮒ؟۰ﻟ؟۰ﮒ؟ﮔﺅﺙﮔ۴ﮒﮒﺓﺎﻛﺟﮒﮒ? {output_file}")

        

        # ﻝﮔﮒ؟۰ﻟ؟۰ﮔﻟ۵ﮔ۴ﮒ

        generate_summary_report(results, timestamp)

        

        return 0

        

    except Exception as e:

logger.error(f"ﮔﮒﮒ؟۰ﻟ؟۰ﮒ۳ﺎﻟﺑ۴: {str(e)}")

        return 1



def generate_summary_report(results, timestamp):

    """ﻝﮔﮒ؟۰ﻟ؟۰ﮔﻟ۵ﮔ۴ﮒ"""

    summary_file = f'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/monthly_summary_{timestamp}.md'

    

    with open(summary_file, 'w', encoding='utf-8') as f:

        f.write(f"# ﮔﮒﭦ۵ﮔﮔ۰۲ﮒ؟۰ﻟ؟۰ﮔﻟ۵ﮔ۴ﮒ\n\n")

        f.write(f"**ﮒ؟۰ﻟ؟۰ﮔﭘﻠﺑ**: {results['summary']['scan_time']}\n\n")

        f.write(f"## ﮒ؟۰ﻟ؟۰ﮔ۵ﻟ۵\n\n")

        f.write(f"- ﮔ،ﮔﮔﻛﭨﭘﮔ? {results['summary']['scanned_files']}\n")

        f.write(f"- ﻠ؟ﻠ۱ﮔﭨﮔﺍ: {results['summary']['total_issues']}\n\n")

        

        if results['summary']['issues_by_severity']:

            f.write(f"## ﻠ؟ﻠ۱ﮒﮒﺕ\n\n")

            for severity, count in results['summary']['issues_by_severity'].items():

                f.write(f"- {severity}: {count}ﻛﺕ۹\n")

        

        if results['summary']['issues_by_type']:

            f.write(f"\n## ﻠ؟ﻠ۱ﻝﺎﭨﮒ\n\n")

            for issue_type, count in results['summary']['issues_by_type'].items():

                f.write(f"- {issue_type}: {count}ﻛﺕ۹\n")



if __name__ == '__main__':

    sys.exit(run_standard_audit())

```



### 3.3 ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﻟﮔ؛



**ﮔﻛﭨﭘ**: `scripts/scheduled_deep_audit.py`



```python

#!/usr/bin/env python3

"""

ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﻟﮔ؛

ﮒﻟﺛ: ﮔﺁﮒ۲ﮒﭦ۵ﮔ۶ﻟ۰ﺅﺙﮔ۶ﻟ۰ﻛﺕﮒﺎﮒ؟۰ﻟ؟۰ﺅﺙL1-L3ﺅﺙﮒﻛﭦﮒ۳۶ﮒﮒﻝ؛۵ﮒﮔ۶ﮔ۲ﮔ?

"""



import os

import sys

import json

import logging

from datetime import datetime

from pathlib import Path



sys.path.insert(0, str(Path(__file__).parent.parent))



from scripts.document_auditor import DocumentAuditor



logging.basicConfig(

    level=logging.INFO,

    format='%(asctime)s - %(levelname)s - %(message)s',

    handlers=[

        logging.FileHandler('logs/deep_audit.log'),

        logging.StreamHandler()

    ]

)



logger = logging.getLogger(__name__)



def run_deep_audit():

    """ﮔ۶ﻟ۰ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰"""

    try:

        logger.info("ﮒﺙﮒ۶ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟?..")

        

        auditor = DocumentAuditor(project_root='.')

        

        # ﮔ۶ﻟ۰ﻛﺕﮒﺎﮒ؟۰ﻟ؟۰

        l1_results = auditor.audit_layer1_file_system()

        l2_results = auditor.audit_layer2_content()

        l3_results = auditor.audit_layer3_professional_standards()

        

        # ﮒﮒﺗﭘﻝﭨﮔ

        results = {

            'summary': {

                'scan_time': datetime.now().isoformat(),

                'audit_type': 'deep_audit',

                'l1_issues': len(l1_results.get('issues', [])),

                'l2_issues': len(l2_results.get('issues', [])),

                'l3_issues': len(l3_results.get('issues', [])),

                'total_issues': len(l1_results.get('issues', [])) + 

                               len(l2_results.get('issues', [])) + 

                               len(l3_results.get('issues', []))

            },

            'l1_results': l1_results,

            'l2_results': l2_results,

            'l3_results': l3_results

        }

        

        timestamp = datetime.now().strftime('%Y%m%d')

        output_file = f'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/quarterly_{timestamp}.json'

        

        with open(output_file, 'w', encoding='utf-8') as f:

            json.dump(results, f, indent=2, ensure_ascii=False)

        

logger.info(f"ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﮒ؟ﮔﺅﺙﮔ۴ﮒﮒﺓﺎﻛﺟﮒﮒ? {output_file}")

        

        # ﻝﮔﻟﺁ۵ﻝﭨﮔ۴ﮒ

        generate_detailed_report(results, timestamp)

        

        return 0

        

    except Exception as e:

        logger.error(f"ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﮒ۳ﺎﻟﺑ۴: {str(e)}")

        return 1



def generate_detailed_report(results, timestamp):

    """ﻝﮔﻟﺁ۵ﻝﭨﮒ؟۰ﻟ؟۰ﮔ۴ﮒ"""

    report_file = f'docs/09_AUDIT/REPORTS/QUARTERLY_AUDIT_REPORT_{timestamp}.md'

    

    with open(report_file, 'w', encoding='utf-8') as f:

f.write(f"# ﮒ۲ﮒﭦ۵ﮔﮔ۰۲ﮔﺎﭨﻝﮒ؟۰ﻟ؟۰ﮔ۴ﮒ\n\n")

        f.write(f"**ﮒ؟۰ﻟ؟۰ﮔﭘﻠﺑ**: {results['summary']['scan_time']}\n")

        f.write(f"**ﮒ؟۰ﻟ؟۰ﻝﺎﭨﮒ**: ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰\n\n")

        

        f.write(f"## ﮒ؟۰ﻟ؟۰ﮔ۵ﻟ۵\n\n")

        f.write(f"| ﮒ؟۰ﻟ؟۰ﮒﺎﻝﭦ۶ | ﻠ؟ﻠ۱ﮔﺍﻠ |\n")

        f.write(f"|---------|---------|\n")

        f.write(f"| L1ﮔﻛﭨﭘﻝﺏﭨﻝﭨﮒﺎ?| {results['summary']['l1_issues']} |\n")

        f.write(f"| L2ﮔﮔ۰۲ﮒﮒ؟ﺗﮒﺎ?| {results['summary']['l2_issues']} |\n")

f.write(f"| L3ﻛﺕﻛﺕﮔﮒﮒﺎ?| {results['summary']['l3_issues']} |\n")

        f.write(f"| **ﮔﭨﻟ؟۰** | **{results['summary']['total_issues']}** |\n\n")

        

        # L1ﻝﭨﮔﻟﺁ۵ﮔ

        if results['l1_results'].get('issues'):

            f.write(f"## L1ﮔﻛﭨﭘﻝﺏﭨﻝﭨﮒﺎﮒ؟۰ﻟ؟۰ﻝﭨﮔ\n\n")

            for issue in results['l1_results']['issues']:

                f.write(f"- **{issue['file_path']}**: {issue['message']}\n")

        

        # L2ﻝﭨﮔﻟﺁ۵ﮔ

        if results['l2_results'].get('issues'):

            f.write(f"\n## L2ﮔﮔ۰۲ﮒﮒ؟ﺗﮒﺎﮒ؟۰ﻟ؟۰ﻝﭨﮔ\n\n")

            for issue in results['l2_results']['issues']:

                f.write(f"- **{issue['file_path']}**: {issue['message']}\n")

        

        # L3ﻝﭨﮔﻟﺁ۵ﮔ

        if results['l3_results'].get('issues'):

f.write(f"\n## L3ﻛﺕﻛﺕﮔﮒﮒﺎﮒ؟۰ﻟ؟۰ﻝﭨﮔ\n\n")

            for issue in results['l3_results']['issues']:

                f.write(f"- **{issue['file_path']}**: {issue['message']}\n")



if __name__ == '__main__':

    sys.exit(run_deep_audit())

```



---



## 4. ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﮒﺛﮔ۰۲ﻝﻝ۴



### 4.1 ﮔ۴ﮒﻛﺟﻝﻝﻝ۴



| ﮔ۴ﮒﻝﺎﭨﮒ | ﻛﺟﻝﮔﻠ | ﮒﺛﮔ۰۲ﻛﺛﻝﺛ؟ |

|---------|---------|---------|

| **ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?* | 3ﻛﺕ۹ﮔ | audit_reports/weekly/ |

| **ﮔﮒﮒ؟۰ﻟ؟۰ﮔ۴ﮒ** | 1ﮒﺗ?| audit_reports/monthly/ |

| **ﮔﺓﺎﮒﭦ۵ﮒ؟۰ﻟ؟۰ﮔ۴ﮒ** | ﮔﺍﺕﻛﺗ | audit_reports/quarterly/ |

| **ﻛﺕﻠ۰ﺗﮒ؟۰ﻟ؟۰ﮔ۴ﮒ** | ﮔﺍﺕﻛﺗ | audit_reports/adhoc/ |



### 4.2 ﮔ۴ﮒﮔﺕﻝﻟﮔ؛



**ﮔﻛﭨﭘ**: `scripts/cleanup_audit_reports.py`



```python

#!/usr/bin/env python3

"""

ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﮔﺕﻝﻟﮔ؛

ﮒﻟﺛ: ﮔﺕﻝﻟﺟﮔﻝﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?

"""



import os

import shutil

from datetime import datetime, timedelta

from pathlib import Path



def cleanup_old_reports():

    """ﮔﺕﻝﻟﺟﮔﻝﮒ؟۰ﻟ؟۰ﮔ۴ﮒ?""

    base_path = Path('docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state')

    

    # ﮔﺕﻝﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺅﺙﻛﺟﻝ3ﻛﺕ۹ﮔﺅﺙ?

    weekly_path = base_path / 'weekly'

    if weekly_path.exists():

        cleanup_reports(weekly_path, days=90)

    

# ﮔﺕﻝﮔﮒﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺅﺙﻛﺟﻝ?ﮒﺗﺑﺅﺙ

    monthly_path = base_path / 'monthly'

    if monthly_path.exists():

        cleanup_reports(monthly_path, days=365)



def cleanup_reports(directory, days):

"""ﮔﺕﻝﮔﮒ؟ﻝ؟ﮒﺛﻛﺕﻟﭘﻟﺟﮔﮒ؟ﮒ۳۸ﮔﺍﻝﮔ۴ﮒ"""

    cutoff_date = datetime.now() - timedelta(days=days)

    

    for file_path in directory.glob('*.json'):

        file_date = datetime.fromtimestamp(file_path.stat().st_mtime)

        

        if file_date < cutoff_date:

            file_path.unlink()

print(f"ﮒﺓﺎﮒﻠ۳ﻟﺟﮔﮔ۴ﮒ? {file_path}")



if __name__ == '__main__':

    cleanup_old_reports()

```



---



## 5. ﮒ؟۰ﻟ؟۰ﻠﻝ۴ﻠﻝﺛ؟



### 5.1 ﻠ؟ﻛﭨﭘﻠﻝ۴ﻠﻝﺛ؟



**ﮔﻛﭨﭘ**: `config/audit_notification.yaml`



```yaml

email:

  enabled: true

  smtp_server: "smtp.example.com"

  smtp_port: 587

  sender: "audit@example.com"

  recipients:

    - "architect@example.com"

    - "doc-admin@example.com"

  

  subject_template: "ZephyrAlphaﮔﮔ۰۲ﮒ؟۰ﻟ؟۰ﮔ۴ﮒ - {audit_type} - {date}"

  

  body_template: |

    ﮒﺍﮔ؛ﻝﮔﮔ۰۲ﻝ؟۰ﻝﮒﺅﺙ?

    

    {audit_type}ﮒ؟۰ﻟ؟۰ﮒﺓﺎﮒ؟ﮔﺅﺙﻛﭨ۴ﻛﺕﮔﺁﮒ؟۰ﻟ؟۰ﻝﭨﮔﮔﻟ۵ﺅﺙ

    

    - ﮔ،ﮔﮔﻛﭨﭘﮔ? {scanned_files}

    - ﻠ؟ﻠ۱ﮔﭨﮔﺍ: {total_issues}

    - ﻛﺕ۴ﻠﻠ؟ﻠ۱: {critical_issues}

- ﻟ۵ﮒﻠ؟ﻠ۱: {warning_issues}

    

    ﻟﺁ۵ﻝﭨﮔ۴ﮒﻟﺁﺓﮔ۴ﻝ? {report_path}

    

ﮔ۳ﻟﺑ

    Audit Sentinel

```



### 5.2 ﻠﻠﻠﻝ۴ﻠﻝﺛ؟



```yaml

dingtalk:

  enabled: true

  webhook: "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"

  

  message_template: |

    {

      "msgtype": "markdown",

      "markdown": {

        "title": "ﮔﮔ۰۲ﮒ؟۰ﻟ؟۰ﮔ۴ﮒ",

<!-- ﮒﻛﺛﻝ؛۵ﻠﺝﮔ۴ﮒﺓﺎﮔﺏ۷ﻠ: "text": "### {audit_type}ﮒ؟۰ﻟ؟۰ﮒ؟ﮔ\n\n- ﮔ،ﮔﮔﻛﭨﭘﮔ? {scanned_files}\n- ﻠ؟ﻠ۱ﮔﭨﮔﺍ: {total_issues}\n- ﻛﺕ۴ﻠﻠ؟ﻠ۱: {critical_issues}\n\nﮔ۴ﻝﻟﺁ۵ﻝﭨﮔ۴ﮒ" -->



      }

    }

```



---



## 6. ﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻝﮔ۶



### 6.1 ﻛﭨﭨﮒ۰ﮔ۶ﻟ۰ﻝﭘﮔﮔ۲ﮔ?



**ﮔﻛﭨﭘ**: `scripts/check_audit_status.py`



```python

#!/usr/bin/env python3

"""

ﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻝﭘﮔﮔ۲ﮔ۴ﻟﮔ?

ﮒﻟﺛ: ﮔ۲ﮔ۴ﮒ؟ﮔﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﮔﺁﮒ۵ﮔ۲ﮒﺕﺕﮔ۶ﻟ۰?

"""



import os

from datetime import datetime, timedelta

from pathlib import Path



def check_audit_status():

    """ﮔ۲ﮔ۴ﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﻝﭘﮔ?""

    base_path = Path('docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state')

    

    # ﮔ۲ﮔ۴ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﺅﺙﮒﭦﻟﺁ۴ﮔﺁﮒ۷ﮔ۶ﻟ۰ﺅﺙ?

    latest_weekly = get_latest_report(base_path / 'weekly')

    if latest_weekly:

        days_since_last = (datetime.now() - latest_weekly).days

        if days_since_last > 7:

print(f"ﻗﺅﺕ  ﻟ۵ﮒ: ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﮒﺓﺎ {days_since_last} ﮒ۳۸ﮔ۹ﮔ۶ﻟ۰")

        else:

print(f"ﻗ?ﮒﺟ،ﻠﮒ؟۰ﻟ؟۰ﻝﭘﮔﮔ۲ﮒﺕﺕﺅﺙﻛﺕﮔ؛۰ﮔ۶ﻟ۰: {latest_weekly}")

    

# ﮔ۲ﮔ۴ﮔﮒﮒ؟۰ﻟ؟۰ﺅﺙﮒﭦﻟﺁ۴ﮔﺁﮔﮔ۶ﻟ۰ﺅﺙ?

    latest_monthly = get_latest_report(base_path / 'monthly')

    if latest_monthly:

        days_since_last = (datetime.now() - latest_monthly).days

        if days_since_last > 30:

print(f"ﻗﺅﺕ  ﻟ۵ﮒ: ﮔﮒﮒ؟۰ﻟ؟۰ﮒﺓ?{days_since_last} ﮒ۳۸ﮔ۹ﮔ۶ﻟ۰")

        else:

print(f"ﻗ?ﮔﮒﮒ؟۰ﻟ؟۰ﻝﭘﮔﮔ۲ﮒﺕﺕﺅﺙﻛﺕﮔ؛۰ﮔ۶ﻟ۰: {latest_monthly}")



def get_latest_report(directory):

    """ﻟﺓﮒﮔﮔﺍﻝﮒ؟۰ﻟ؟۰ﮔ۴ﮒﮔﭘﻠﺑ"""

    if not directory.exists():

        return None

    

    latest_time = None

    for file_path in directory.glob('*.json'):

        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)

        if latest_time is None or file_time > latest_time:

            latest_time = file_time

    

    return latest_time



if __name__ == '__main__':

    check_audit_status()

```



---



## 7. ﮔﻠﮔ۱ﮒ۳



### 7.1 ﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﮒ۳ﺎﻟﺑ۴ﮒ۳ﻝ



ﮒ۵ﮔﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰ﮒ۳ﺎﻟﺑ۴ﺅﺙﮔ۶ﻟ۰ﻛﭨ۴ﻛﺕﮔ۴ﻠ۹۳ﺅﺙ



1. **ﮔ۲ﮔ۴ﮔ۴ﮒﺟﮔﻛﭨ?*:

   ```bash

   tail -f logs/audit.log

   ```



2. **ﮔﮒ۷ﮔ۶ﻟ۰ﮒ؟۰ﻟ؟۰**:

   ```bash

   python scripts/document_auditor.py --quick

   ```



3. **ﮔ۲ﮔ۴ﻝﺏﭨﻝﭨﻟﭖﮔﭦ?*:

   ```bash

   df -h  # ﮔ۲ﮔ۴ﻝ۲ﻝﻝ۸ﭦﻠ?

free -m  # ﮔ۲ﮔ۴ﮒﮒ?

   ```



4. **ﻠﮒﺁﮒ؟۰ﻟ؟۰ﻛﭨﭨﮒ۰**:

   ```bash

   # Linux

   sudo systemctl restart cron

   

   # Windows

# ﮒ۷ﻛﭨﭨﮒ۰ﻟ؟۰ﮒﻝ۷ﮒﭦﻛﺕﮔﮒ۷ﻟﺟﻟ۰ﻛﭨﭨﮒ۰

   ```



---



## 8. ﮒﻟﮔﮔ۰?



- ﮔﮔ۰۲ﮔﺎﭨﻝﮔﭖﻝ۷ﮔﮒ

- ﮔﮔ۰۲ﮒ؟۰ﻟ؟۰ﮒﺓ۴ﮒﺓﻛﺛﺟﻝ۷ﮔﮒ



---



**ﻠﻝﺛ؟ﻝﭘﮔ?*: ﮔ۲ﮒﺙﮔﮒ

**ﻛﺕﮔ؛۰ﮒ؟۰ﮔ۴**: 2026-07-02

