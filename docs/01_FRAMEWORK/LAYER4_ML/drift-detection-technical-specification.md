---
module_id: DRIFT_DETECTION_TECHNICAL_SPECIFICATION
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - DRIFT_DETECTION_TECHNICAL技术规范
layer: layer_01
spec_version: 1.0
parent_doc: docs/01_FRAMEWORK/DRIFT_DETECTION_BLUEPRINT.md
index: DD-001
estimated_hours: 30
review_status: Pending
reviewer: ﻠ۵ﮒﺕﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
review_date: 2026-04-03
applicable_scope: "ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻝﺏﭨ?compliance_level: ﻠ۰ﭘﻝﭦ۶ﻛﺕﻛﺕﮔﮒ"
parent_document: ../01_FRAMEWORK/DRIFT_DETECTION_BLUEPRINT.md
implementation_status: ﮔﮔﺁﻟ۶ﮔﺙﻟ؟ﺝﻟ؟۰ﮒ؟?
---
---



# ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵ v1.0

> **核心职责**: 定义drift detection technical specification的技术规格、接口标准和实现细节

> **职责边界**: 

> - ✅ 本文档负责：文档内容说明相关内容

> - ❌ 本文档不负责：其他模块内容





> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.3 - ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻟﺁ۵ﻝﭨﮔﮔﺁﻟ؟ﺝ?> **ﻝﺑ۱ﮒﺙ**: `DD-001`

> **ﮒﺙﮒﮔﭘ?*: 30h

> **ﮔﺕﮒﺟﮒ؟ﻛﺛ**: ﮔﻛﺝﻝﺗﮒﺝﮔﺙﻝ۶ﭨﻙﮔ۵ﮒﺟﭖﮔﺙﻝ۶ﭨﮒﻠ۱ﮔﭖﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻟﺛ?---





## 1. ﮔ۵ﻟﺟﺍ



### 1.1 ﻟ؟ﺝﻟ؟۰ﻟﮔﺁﻛﺕﻛﺕﮒ۰ﻝ؟?

**ﻛﺕﮒ۰ﻠ?*?- ﻠﻟﮒﺕﮒﭦﮔﺍﮔ؟ﮒﮒﺕﻠﮔﭘﻠﺑﮒﮒﺅﺙﮔ۷۰ﮒﮔ۶ﻟﺛﻛﺙﻠﮔﺕﻠ?- ﻠﻟ۵ﮒﮔﭘﮒﻝﺍﮔﺍﮔ؟ﮒﮒﺕﮒﮒﺅﺙﻟ۶۵ﮒﮔ۷۰ﮒﻠﮔﺍﻟ؟ﻝﭨ

- ﮒﭨﭦﻝ،ﮔﺍﮔ؟ﻟﺑ۷ﻠﻝﮔ۶ﻛﺛﻝﺏﭨﺅﺙﻛﺟﻠﮔ۷۰ﮒﻟﺝﮒ۴ﮔﺍﮔ؟ﻝ۷ﺏﮒ؟?

**ﮔﮔﺁﻝ?*?- ﮒﺛﮒﻝﺙﭦﻛﺗﻝﺏﭨﻝﭨﮒﻝﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮔﭦ?- ﮔ۷۰ﮒﮔ۶ﻟﺛﻠﮒﻠﺝﻛﭨ۴ﮔ۸ﮔﮒ?- ﮔﺍﮔ؟ﻟﺑ۷ﻠﻠ؟ﻠ۱ﮒﺛﺎﮒﮔ۷۰ﮒﮔﮔ



**ﻠ۱ﮔﻛﭨ?*?- ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮒﻝ۰؟ﻝ?0%

- ﮔ۷۰ﮒﮔ۶ﻟﺛﻠﮒﻠ۱ﻟ۵ﮔﮒﻠ??- ﮔﺍﮔ؟ﻟﺑ۷ﻠﻠ؟ﻠ۱ﮒﻝﺍﻝﮔ?0%



### 1.2 ﮔﮔﺁﮒ؟ﻛﺛﻛﺕﮔﭘﮔﮒﺎﮒﺛ?

- **Layerﮒ؟ﻛﺛ**: Layer 4 - ﮔﭦﮒ۷ﮒ۵ﻛﺗ?(AIﮔ۷۰ﮒﮔﮒ۰)

- **ﮔ۷۰ﮒﻝﺎﭨﮒ،**: ﮔﺕﮒﺟﮔﺁﮔﮔ۷۰ﮒ

- **ﮔﭘﮔﻟ۶ﻟﺎ**: ﮔﻛﺝﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻙﮒﻟ۵ﮒﻟ۶۵ﮒﮔﭦﮒﭘ



### 1.3 ﻝﮔ؛ﻛﺟ۰ﮔﺁﻛﺕﮒﮔﺑﻟ؟ﺍ?

| ﻝﮔ؛ | ﮔ۴ﮔ | ﻛﺛ?| ﮒﮔﺑﻟﺁﺑﮔ | ﻝ?|

|------|------|------|----------|------|

| v1.0 | 2026-04-03 | AIﮒﺓ۴ﻝ۷?| ﮒﮒ۶ﻝﮔ؛ | Active |



---

## 2. ﻟﺁ۵ﻝﭨﮔﭘﮔﻟ؟ﺝﻟ؟۰



### 2.1 ﻝﺏﭨﻝﭨﮔﭘﮔ?

```

ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ??                   ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻝﺏﭨﻝﭨﮔﭘ?                         ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ??                                                                ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?? ?             ﮔﺍﮔ؟ﻟﺝﮒ۴?(Data Input Layer)               ? ?? ? ﻗﻗﻗ ReferenceDataLoader (ﮒﭦﮒﮔﺍﮔ؟ﮒﻟﺛﺛ)                  ? ?? ? ﻗﻗﻗ CurrentDataLoader (ﮒﺛﮒﮔﺍﮔ؟ﮒﻟﺛﺛ)                    ? ?? ? ﻗﻗﻗ DataPreprocessor (ﮔﺍﮔ؟ﻠ۱ﮒ۳?                       ? ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ??                             ?                                 ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?? ?             ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮒﺎ (Drift Detection Layer)          ? ?? ? ﻗﻗﻗ FeatureDriftDetector (ﻝﺗﮒﺝﮔﺙﻝ۶ﭨﮔ۲?                 ? ?? ? ﻗﻗﻗ ConceptDriftDetector (ﮔ۵ﮒﺟﭖﮔﺙﻝ۶ﭨﮔ۲?                 ? ?? ? ﻗﻗﻗ PredictionDriftDetector (ﻠ۱ﮔﭖﮔﺙﻝ۶ﭨﮔ۲?              ? ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ??                             ?                                 ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?? ?             ﮒﻟ۵ﻛﺕﮒﮒﭦﮒﺎ (Alert & Response Layer)       ? ?? ? ﻗﻗﻗ DriftAlertManager (ﮔﺙﻝ۶ﭨﮒﻟ۵ﻝ؟۰ﻝ)                    ? ?? ? ﻗﻗﻗ RetrainingTrigger (ﻠﻟ؟ﻝﭨﻟ۶۵?                      ? ?? ? ﻗﻗﻗ DriftReportGenerator (ﮔﺙﻝ۶ﭨﮔ۴ﮒﻝﮔ)                 ? ?? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ??                                                                ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```



### 2.2 Layerﮒ؟ﻛﺛﻟﺁ۵ﻝﭨﻟﺁﺑﮔ



- **Layerﮒﺛﮒﺎ**: Layer 4 - ﮔﭦﮒ۷ﮒ۵ﻛﺗ?- **ﻟﻟﺑ۲ﻟﮒﺑ**: ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻙﮒﻟ۵ﻠﻝ۴ﻙﻠﻟ؟ﻝﭨﻟ۶۵ﮒ

- **ﻛﺕﻛﺕﮒﺎﮔ۴?*: 

- ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 7 (ﻝﻝ۴? - ﮔﺙﻝ۶ﭨﻝﭘﮔﮔ۴?  - ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 4 (ﮔﺍﮔ؟? - ﻝﺗﮒﺝﮔﺍﮔ؟



### 2.3 ﮔ۷۰ﮒﻟﻟﺑ۲ﻛﺕﻟﺝﺗﻝﮒ؟?

- **ﮔﺕﮒﺟﻟﻟﺑ۲**: ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮒﮒﻟ۵

- **ﻟﻟﺑ۲ﻟﺝﺗﻝ**: 

- ?ﮔ؛ﮔ۷۰ﮒﻟﺑ? ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻙﮒﻟ۵ﻠﻝ۴ﻙﻠﻟ؟ﻝﭨﻟ۶۵ﮒ

- ?ﮔ؛ﮔ۷۰ﮒﻛﺕﻟﺑﻟﺑ۲: ﮔ۷۰ﮒﻟ؟ﻝﭨﻙﻝﺗﮒﺝﮒﺓ۴ﻝ۷ﻙﮔﺍﮔ؟ﮔﺕ?- **ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵**: ﮔﻛﺝﮔﮒﮒﻝﮔﺙﻝ۶ﭨﮔ۲ﮔﭖAPI



### 2.4 ﻛﺝﻟﭖﮒﺏﻝﺏﭨﻛﺕﻠﮔﻝﺗ



| ﻛﺝﻟﭖﮔ۷۰ﮒ | ﻛﺝﻟﭖﻝﺎﭨﮒ | ﮔ۴ﮒ۲ﮔﺗﮒﺙ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﮒ۳ﮔﺏ۷ |

|----------|----------|----------|----------|------|

| Evidently | ﮒﺙﭦﻛﺝ?| Python?| >=0.4.0 | ﮔﺙﻝ۶ﭨﮔ۲?|

| Scipy | ﮒﺙﭦﻛﺝ?| Python?| >=1.11.0 | ﻝﭨﻟ؟۰ﮔ۲?|

| Numpy | ﮒﺙﭦﻛﺝ?| Python?| >=1.24.0 | ﮔﺍﮒﺙﻟ؟۰?|

| Pandas | ﮒﺙﭦﻛﺝ?| Python?| >=2.0.0 | ﮔﺍﮔ؟ﮒ۳ﻝ |



---



## 3. ﮔ۴ﮒ۲ﮒ؟ﻛﺗ



### 3.1 APIﮔ۴ﮒ۲ﻟ۶ﻟ



```python

from typing import Dict, Any, List, Optional

from dataclasses import dataclass

from datetime import datetime

from enum import Enum

from pydantic import BaseModel, Field

import numpy as np

import pandas as pd





class DriftType(Enum):

    """ﮔﺙﻝ۶ﭨﻝﺎﭨﮒ"""

    FEATURE_DRIFT = "feature_drift"

    CONCEPT_DRIFT = "concept_drift"

    PREDICTION_DRIFT = "prediction_drift"





class DriftSeverity(Enum):

    """ﮔﺙﻝ۶ﭨﻛﺕ۴ﻠﻝ۷ﮒﭦ۵"""

    NONE = "none"

    LOW = "low"

    MEDIUM = "medium"

    HIGH = "high"

    CRITICAL = "critical"





class DriftResult(BaseModel):

    """ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻝﭨ?""

    drift_type: DriftType

    feature_name: Optional[str] = None

    drift_detected: bool

    severity: DriftSeverity

    statistic_value: float

    p_value: float

    threshold: float

    timestamp: datetime

    details: Dict[str, Any] = Field(default_factory=dict)





class DriftDetectionRequest(BaseModel):

    """ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻟﺁﺓ?""

    model_id: str

    reference_data_start: datetime

    reference_data_end: datetime

    current_data_start: datetime

    current_data_end: datetime

    features: Optional[List[str]] = None

    detection_methods: List[str] = Field(default=["ks", "psi"])





class DriftDetectionResponse(BaseModel):

    """ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮒ?""

    model_id: str

    drift_results: List[DriftResult]

    overall_drift_score: float

    recommendation: str





class DriftReportRequest(BaseModel):

    """ﮔﺙﻝ۶ﭨﮔ۴ﮒﻟﺁﺓﮔﺎ"""

    model_id: str

    report_type: str = Field(default="summary")

    time_range: str = Field(default="7d")





class DriftReportResponse(BaseModel):

    """ﮔﺙﻝ۶ﭨﮔ۴ﮒﮒﮒﭦ"""

    model_id: str

    report_id: str

    report_url: str

    summary: Dict[str, Any]





class DataDriftDetectorAPI:

    """ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖAPI"""

    

    def detect_feature_drift(

        self,

        reference_data: pd.DataFrame,

        current_data: pd.DataFrame,

        features: List[str],

        methods: List[str] = ["ks", "psi"]

    ) -> List[DriftResult]:

        """

        ﮔ۲ﮔﭖﻝﺗﮒﺝﮔﺙ?        

        Args:

            reference_data: ﮒﭦﮒﮔﺍﮔ؟

            current_data: ﮒﺛﮒﮔﺍﮔ؟

            features: ﻝﺗﮒﺝﮒﻟ۰۷

            methods: ﮔ۲ﮔﭖﮔﺗﮔﺏﮒ?            

        Returns:

            ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻝﭨﮔﮒ?        """

        pass

    

    def detect_concept_drift(

        self,

        predictions: np.ndarray,

        ground_truth: np.ndarray,

        window_size: int = 100

    ) -> DriftResult:

        """

        ﮔ۲ﮔﭖﮔ۵ﮒﺟﭖﮔﺙ?        

        Args:

            predictions: ﻠ۱ﮔﭖﻝﭨﮔ

ground_truth: ﻝﮒ؟ﮔﻝﺝ

            window_size: ﮔﭨﮒ۷ﻝ۹ﮒ۲ﮒ۳۶ﮒﺍ

            

        Returns:

            ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻝﭨ?        """

        pass

    

    def detect_prediction_drift(

        self,

        reference_predictions: np.ndarray,

        current_predictions: np.ndarray

    ) -> DriftResult:

        """

        ﮔ۲ﮔﭖﻠ۱ﮔﭖﮔﺙ?        

        Args:

            reference_predictions: ﮒﭦﮒﻠ۱ﮔﭖ

            current_predictions: ﮒﺛﮒﻠ۱ﮔﭖ

            

        Returns:

            ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻝﭨ?        """

        pass

    

    def generate_drift_report(

        self,

        request: DriftReportRequest

    ) -> DriftReportResponse:

        """

        ﻝﮔﮔﺙﻝ۶ﭨﮔ۴ﮒ

        

        Args:

            request: ﮔ۴ﮒﻟﺁﺓﮔﺎ

            

        Returns:

            ﮔ۴ﮒﮒﮒﭦ

        """

        pass

    

    def get_drift_history(

        self,

        model_id: str,

        time_range: str = "7d"

    ) -> List[DriftResult]:

        """

        ﻟﺓﮒﮔﺙﻝ۶ﭨﮒﮒﺎ

        

        Args:

            model_id: ﮔ۷۰ﮒID

            time_range: ﮔﭘﻠﺑﻟﮒﺑ

            

        Returns:

            ﮔﺙﻝ۶ﭨﮒﮒﺎﮒﻟ۰۷

        """

        pass

```



### 3.2 ﮔﺍﮔ؟ﮔﺙﮒﺙﻛﺕﮒﻟ؟؟ﮒ؟?

```json

{

  "drift_detection_request": {

    "model_id": "signal_model_v1",

    "reference_data_start": "2026-03-01T00:00:00Z",

    "reference_data_end": "2026-03-31T00:00:00Z",

    "current_data_start": "2026-04-01T00:00:00Z",

    "current_data_end": "2026-04-03T00:00:00Z",

    "features": ["momentum", "volatility", "volume"],

    "detection_methods": ["ks", "psi"]

  },

  "drift_detection_response": {

    "model_id": "signal_model_v1",

    "drift_results": [

      {

        "drift_type": "feature_drift",

        "feature_name": "momentum",

        "drift_detected": true,

        "severity": "medium",

        "statistic_value": 0.15,

        "p_value": 0.02,

        "threshold": 0.05

      }

    ],

    "overall_drift_score": 0.35,

"recommendation": "ﮒﭨﭦﻟ؟؟ﻠﮔﺍﻟ؟ﻝﭨﮔ۷۰ﮒ"

  }

}

```



### 3.3 ﮔ۶ﻟﺛﮔﮔﻛﺕSLAﻟ۵ﮔﺎ



| ﮔﮔ | ﻝ؟ﮔ?| ﮔﭖﻠﮔﺗﮔﺏ | ﮒ۳ﮔﺏ۷ |

|------|--------|----------|------|

| **ﮔ۲ﮔﭖﮒﭨﭘ?* | ?0?| ﻝ،ﺁﮒﺍﻝ،ﺁﮒﭨﭘ?| ﮔﺕﮒﺟﮔ۴ﮒ۲ |

| **ﮔ۲ﮔﭖﮒﻝ۰؟ﻝ** | ?0% | ﮒﺁﺗﮔﺁﻠ۹ﻟﺁ | ﮒﻝ۰؟ﮔ۶ﻟ۵?|

| **ﻟﺁﺁﮔ۴?* | ?% | ﻝﭨﻟ؟۰ﮒﮔ | ﮒﺁﻠﮔ۶ﻟ۵?|

| **ﮒﺁﻝ۷?* | ?9.9% | ﮔﺁﮔﮒ؟ﮔﭦﮔﭘﻠﺑ | SLAﻟ۵ﮔﺎ |



### 3.4 ﮒ؟ﮒ۷ﻛﺕﻟ؟۳ﻟﺁﮔﭦ?

- **ﻟ؟۳ﻟﺁﮔﺗﮒﺙ**: APIﮒﺁﻠ۴ﻟ؟۳ﻟﺁ

- **ﮔﮔﮔﭦﮒﭘ**: ﮒﭦﻛﭦﻟ۶ﻟﺎﻝﻟ؟ﺟﻠ؟ﮔ۶?- **ﮔﺍﮔ؟ﮒﮒﺁ**: TLS 1.3ﻛﺙﻟﺝﮒﮒﺁ

- **ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ**: ﮔﮔﮔﻛﺛﻟ؟ﺍﮒﺛﮒ؟۰ﻟ؟۰ﮔ۴?

---



## 4. ﮔﺍﮔ؟ﮔ۷۰ﮒﻛﺕﮒ?

### 4.1 ﮔﺍﮔ؟ﮒﭦﻟ۰۷ﻝﭨﮔﻟ؟ﺝﻟ؟۰



```sql

CREATE TABLE IF NOT EXISTS drift_detection_history (

    detection_id VARCHAR(64) PRIMARY KEY,

    model_id VARCHAR(64) NOT NULL,

    drift_type VARCHAR(32) NOT NULL,

    feature_name VARCHAR(64),

    drift_detected BOOLEAN NOT NULL,

    severity VARCHAR(16) NOT NULL,

    statistic_value FLOAT,

    p_value FLOAT,

    threshold FLOAT,

    detection_method VARCHAR(32),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_model_time (model_id, created_at),

    INDEX idx_drift_type (drift_type)

);



CREATE TABLE IF NOT EXISTS drift_alerts (

    alert_id VARCHAR(64) PRIMARY KEY,

    model_id VARCHAR(64) NOT NULL,

    detection_id VARCHAR(64),

    severity VARCHAR(16) NOT NULL,

    message TEXT,

    status VARCHAR(16) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    resolved_at TIMESTAMP,

    FOREIGN KEY (detection_id) REFERENCES drift_detection_history(detection_id)

);



CREATE TABLE IF NOT EXISTS retraining_triggers (

    trigger_id VARCHAR(64) PRIMARY KEY,

    model_id VARCHAR(64) NOT NULL,

    detection_id VARCHAR(64),

    trigger_reason TEXT,

    status VARCHAR(16) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    executed_at TIMESTAMP,

    FOREIGN KEY (detection_id) REFERENCES drift_detection_history(detection_id)

);

```



### 4.2 ﮔﺍﮔ؟ﮔﭖﻛﺕETLﮔﭖﻝ۷



```

```



### 4.3 ﻝﺙﮒﻝﻝ۴ﻛﺕﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﮔﺗ?

- **ﻝﺙﮒﻝﺎﭨﮒ**: Redisﮒﮒﺕﮒﺙﻝﺙ?- **ﻝﺙﮒﻝﻝ۴**: LRU + TTL (1ﮒﺍﮔﭘ)

- **ﻛﺕﻟﺑﮔ۶ﻛﺟ?*: ﮔﻝﭨﻛﺕﻟ?- **ﮒ۳ﺎﮔﻝﻝ۴**: ﮔﺍﮔ۲ﮔﭖﮒ؟ﮔﮒﮒ۳ﺎﮔ



### 4.4 ﮒ۳ﻛﭨﺛﻛﺕﮔ۱ﮒ۳ﮔﺗ?

- **ﮒ۳ﻛﭨﺛﻝﻝ۴**: ﮔﺁﮔ۴ﮒ۷ﻠﮒ۳ﻛﭨﺛ

- **ﮔ۱ﮒ۳ﻝﺗﻝ؟?RPO)**: ?4ﮒﺍﮔﭘ

- **ﮔ۱ﮒ۳ﮔﭘﻠﺑﻝ؟ﮔ(RTO)**: ?ﮒﺍﮔﭘ

- **ﻝﺝﻠﺝﮔ۱ﮒ۳**: ﮒﺙﮒﺍﮒ۳ﻛﭨﺛ



---



## 5. ﻝ؟ﮔﺏﮒ؟ﻝﺍﻟﺁﺑﮔ



### 5.1 ﮔﺕﮒﺟﻝ؟ﮔﺏﮒﻝﻛﺕﮔﺍﮒ۵ﮒ؛?

**KSﮔ۲?(Kolmogorov-Smirnov Test)**:

```

ﻝ؟ﮔﺏﮒﻝ۶ﺍ: Kolmogorov-Smirnov Test

ﮔﺍﮒ۵ﮒ؛ﮒﺙ: D = max|F_n(x) - G_m(x)|

ﮒﭘﻛﺕ: F_n(x)ﮔﺁﮒﭦﮒﮔﺍﮔ؟ﻝﺑﺁﻝ۶ﺁﮒﮒﺕﮒﺛ?      G_m(x)ﮔﺁﮒﺛﮒﮔﺍﮔ؟ﻝﺑﺁﻝ۶ﺁﮒﮒﺕﮒﺛ?ﮔﭘﻠﺑﮒ۳ﮔ? O(n log n)

ﻝ۸ﭦﻠﺑﮒ۳ﮔ? O(n)

```



**PSI (Population Stability Index)**:

```

ﻝ؟ﮔﺏﮒﻝ۶ﺍ: Population Stability Index

ﮔﺍﮒ۵ﮒ؛ﮒﺙ: PSI = ﺳ۲((Actual% - Expected%) * ln(Actual%/Expected%))

ﮒ۳ﮔﮔﮒ: PSI < 0.1: ﮔﮔﺝﻟﮔﺙ?         0.1 ?PSI < 0.25: ﻛﺕﻝﮔﺙﻝ۶ﭨ

         PSI ?0.25: ﮔﺝﻟﮔﺙﻝ۶ﭨ

ﮔﭘﻠﺑﮒ۳ﮔ? O(n)

ﻝ۸ﭦﻠﺑﮒ۳ﮔ? O(1)

```



**ADWIN (Adaptive Windowing)**:

```

ﻝ؟ﮔﺏﮒﻝ۶ﺍ: Adaptive Windowing for Concept Drift

ﮒﻝ: ﮒ۷ﮔﻟﺍﮔﺑﻝ۹ﮒ۲ﮒ۳۶ﮒﺍﺅﺙﮔ۲ﮔﭖﮒﮒﺕﮒ?ﮔﭘﻠﺑﮒ۳ﮔ? O(log n)

ﻝ۸ﭦﻠﺑﮒ۳ﮔ? O(log n)

```



### 5.2 ﮔﭘﻠﺑﮒ۳ﮔﮒﭦ۵ﻛﺕﻝ۸ﭦﻠﺑﮒ۳ﮔﮒﭦ۵ﮒ?

| ﮔﻛﺛ | ﮔﭘﻠﺑﮒ۳ﮔ?| ﻝ۸ﭦﻠﺑﮒ۳ﮔ?| ﻟﺁﺑﮔ |

|------|------------|------------|------|

| KSﮔ۲?| O(n log n) | O(n) | nﻛﺕﭦﮔﺓﮔ؛ﮔﺍ |

| PSIﻟ؟۰ﻝ؟ | O(n) | O(1) | ﻝﭦﺟﮔ۶ﮔ،?|

| ADWINﮔ۲?| O(log n) | O(log n) | ﮒ۱ﻠﮔﺑﮔﺍ |

| ﮔﺑﻛﺛﮔ۲?| O(n log n) | O(n) | ﻝﭨﺙﮒﮒ۳ﮔ?|



### 5.3 ﮒﮔﺍﻠﻝﺛ؟ﻛﺕﻟﺍﻛﺙﮔ?

```yaml

drift_detection_params:

  feature_drift:

    ks_test:

      p_value_threshold: 0.05

      significance_level: 0.05

    psi:

      bins: 10

      threshold_low: 0.1

      threshold_high: 0.25

  concept_drift:

    adwin:

      delta: 0.002

      min_window_size: 100

      max_window_size: 10000

  prediction_drift:

    threshold: 0.1

    window_size: 1000

  alert:

    severity_thresholds:

      low: 0.1

      medium: 0.25

      high: 0.5

      critical: 0.75

```



### 5.4 ﮔﭖﻟﺁﻝ۷ﻛﺝﻟ؟ﺝﻟ؟۰



```python

import pytest

import numpy as np

import pandas as pd

from drift_detector import DataDriftDetector, DriftType, DriftSeverity





class TestDataDriftDetector:

    """ﮔﺍﮔ؟ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮒ۷ﮔﭖﻟﺁ"""

    

    def test_feature_drift_detection_no_drift(self):

"""ﮔﭖﻟﺁﮔﮔﺙﻝ۶ﭨﮔ?""

        detector = DataDriftDetector({})

        

        np.random.seed(42)

        reference_data = pd.DataFrame({

            'feature1': np.random.normal(0, 1, 1000),

            'feature2': np.random.normal(5, 2, 1000)

        })

        current_data = pd.DataFrame({

            'feature1': np.random.normal(0, 1, 1000),

            'feature2': np.random.normal(5, 2, 1000)

        })

        

        results = detector.detect_feature_drift(

            reference_data=reference_data,

            current_data=current_data,

            features=['feature1', 'feature2']

        )

        

        for result in results:

            assert result.severity in [DriftSeverity.NONE, DriftSeverity.LOW]

    

    def test_feature_drift_detection_with_drift(self):

        """ﮔﭖﻟﺁﮔﮔﺙﻝ۶ﭨﮔ?""

        detector = DataDriftDetector({})

        

        np.random.seed(42)

        reference_data = pd.DataFrame({

            'feature1': np.random.normal(0, 1, 1000)

        })

        current_data = pd.DataFrame({

            'feature1': np.random.normal(2, 1, 1000)

        })

        

        results = detector.detect_feature_drift(

            reference_data=reference_data,

            current_data=current_data,

            features=['feature1']

        )

        

        assert len(results) == 1

        assert results[0].drift_detected == True

        assert results[0].severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]

    

    def test_concept_drift_detection(self):

        """ﮔﭖﻟﺁﮔ۵ﮒﺟﭖﮔﺙﻝ۶ﭨﮔ۲?""

        detector = DataDriftDetector({})

        

        np.random.seed(42)

        predictions = np.random.randint(0, 2, 1000)

        ground_truth = np.random.randint(0, 2, 1000)

        

        ground_truth[500:] = 1 - ground_truth[500:]

        

        result = detector.detect_concept_drift(

            predictions=predictions,

            ground_truth=ground_truth,

            window_size=100

        )

        

        assert result.drift_type == DriftType.CONCEPT_DRIFT

    

    def test_psi_calculation(self):

        """ﮔﭖﻟﺁPSIﻟ؟۰ﻝ؟"""

        detector = DataDriftDetector({})

        

        reference = np.random.normal(0, 1, 1000)

        current = np.random.normal(0, 1, 1000)

        

        psi = detector._calculate_psi(reference, current)

        

        assert 0 <= psi < 0.1

    

    def test_drift_severity_classification(self):

        """ﮔﭖﻟﺁﮔﺙﻝ۶ﭨﻛﺕ۴ﻠﻝ۷ﮒﭦ۵ﮒﻝﺎﭨ"""

        detector = DataDriftDetector({})

        

        assert detector._classify_severity(0.05) == DriftSeverity.NONE

        assert detector._classify_severity(0.15) == DriftSeverity.MEDIUM

        assert detector._classify_severity(0.35) == DriftSeverity.HIGH

        assert detector._classify_severity(0.85) == DriftSeverity.CRITICAL

```



---



## 6. ﮒ؟ﮔﺛﮔﮔﺁﮔ



### 6.1 ﻝﺙﻝ۷ﻟﺁﻟ۷ﻛﺕﮔ۰ﮔﭘﻝ?

| ﮔﮔﺁﻝﭨ?| ﻝﮔ؛ | ﻠﮔ۸ﻝﻝﺎ | ﮔﺟﻛﭨ۲ﮔﺗﮔ۰ |

|----------|------|----------|----------|

| Python | 3.11+ | ﻝﮔﻝﺏﭨﻝﭨﮒ؟?| - |

| Evidently | 0.4+ | ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻛﺕ?| ﻟ۹ﮒﭨﭦ |

| Scipy | 1.11+ | ﻝﭨﻟ؟۰ﮔ۲?| statsmodels |

| Numpy | 1.24+ | ﮔﺍﮒﺙﻟ؟۰?| - |

| Pandas | 2.0+ | ﮔﺍﮔ؟ﮒ۳ﻝ | - |



### 6.2 ﻝ؛؛ﻛﺕﮔﺗﮒﭦﻛﺝﻟﭖﻛﺕﻝﮔ؛ﻝﭦ۵?

```txt

evidently>=0.4.0

scipy>=1.11.0

numpy>=1.24.0

pandas>=2.0.0

fastapi>=0.104.0

pydantic>=2.5.0

redis>=5.0.0

```



### 6.3 ﮒﺙﮒﻝﺁﮒ۱ﻟ۵?

- **CPU**: 2ﮔﺕﮒﺟﻛﭨ۴ﻛﺕ

- **ﮒﮒ**: 4GBﻛﭨ۴ﻛﺕ

- **ﮒﮒ۷**: 20GB SSDﮒﺁﻝ۷ﻝ۸ﭦﻠﺑ

- **ﮔﻛﺛﻝﺏﭨﻝﭨ**: Windows 10/11, Ubuntu 20.04+



### 6.4 ﻠ۷ﻝﺛﺎﮔﭘﮔﻛﺕﮒﭦﻝ۰ﻟ؟ﺝﮔﺛ



- **ﻠ۷ﻝﺛﺎﮔ۷۰ﮒﺙ**: ﮒ؟ﺗﮒ۷ﮒﻠ۷?(Docker)

- **ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛ**: ﮔ؛ﮒﺍﮔﮒ۰?- **ﻝﮔ۶ﻝﺏﭨﻝﭨ**: Prometheus + Grafana

- **ﮔ۴ﮒﺟﻝﺏﭨﻝﭨ**: ELK Stack



---



## 7. ﮔﭖﻟﺁﻝﻝ۴



### 7.1 ﮒﮒﮔﭖﻟﺁﻟﮒﺑﻛﺕﻟ۵ﻝﻝﻟ۵ﮔﺎ



- **ﻟ۵ﻝﻝﻝ؟?*: ?0% ﻛﭨ۲ﻝﻟ۵ﻝ?- **ﮔﭖﻟﺁﻟﮒﺑ**: ﮔﮔﮒ؛ﮒﺎﮔ۴ﮒ۲ﮒﮔﺕﮒﺟﻝ؟ﮔﺏ

- **ﮔﭖﻟﺁﮔ۰ﮔﭘ**: pytest + coverage

- **ﮔﻝﭨﻠﮔ**: ﮔﺁﮔ؛۰ﮔﻛﭦ۳ﻟ۹ﮒ۷ﻟﺟﻟ۰ﮔﭖﻟﺁ



### 7.2 ﻠﮔﮔﭖﻟﺁﮒﭦﮔﺁﻟ؟ﺝﻟ؟۰



| ﮔﭖﻟﺁﮒﭦﮔﺁ | ﮔﭖﻟﺁﻝ؟ﮔ | ﻠ۱ﮔﻝﭨﮔ | ﻠﻟﺟﮔﮒ |

|----------|----------|----------|----------|

| ﻝﺗﮒﺝﮔﺙﻝ۶ﭨﮔ۲?| ﮔ۲ﮔﭖﻝﺗﮒﺝﮒﮒﺕﮒ?| ﮔ۲ﻝ۰؟ﻟﺁﮒ،ﮔﺙﻝ۶ﭨ | ﮒﻝ۰؟ﻝﻗ۴90% |

| ﮔ۵ﮒﺟﭖﮔﺙﻝ۶ﭨﮔ۲?| ﮔ۲ﮔﭖﮔ۵ﮒﺟﭖﮒ?| ﮔ۲ﻝ۰؟ﻟﺁﮒ،ﮔﺙﻝ۶ﭨ | ﮒﻝ۰؟ﻝﻗ۴85% |

| ﻠ۱ﮔﭖﮔﺙﻝ۶ﭨﮔ۲?| ﮔ۲ﮔﭖﻠ۱ﮔﭖﮒﮒﺕﮒ?| ﮔ۲ﻝ۰؟ﻟﺁﮒ،ﮔﺙﻝ۶ﭨ | ﮒﻝ۰؟ﻝﻗ۴90% |

| ﮒﻟ۵ﻟ۶۵ﮒ | ﮔﺙﻝ۶ﭨﮒﻟ۵ | ﮔ۲ﻝ۰؟ﻟ۶۵ﮒﮒﻟ۵ | ﮒﭨﭘﻟﺟ?0?|



### 7.3 ﮔ۶ﻟﺛﮔﭖﻟﺁﮒﭦﮒﻛﺕﮔ?

```yaml

performance_benchmarks:

  load_test:

    data_size: 100000

    features: 50

    target_time: <30s

  stress_test:

    concurrent_detections: 10

    duration: 10m

    target_error_rate: <1%

```



### 7.4 ﮒ؟ﮒ۷ﮔﭖﻟﺁﮔﺗﮔ۰



- **OWASP Top 10ﻟ۵ﻝ**: ﮒ۷ﻠ۷10ﻠ۰ﺗﮒ؟ﮒ۷ﮔ۲?- **ﮔﺙﮔﺑﮔ،ﮔ**: ﮒ؟ﮔﮒ؟ﮒ۷ﮔ،ﮔ

- **ﮔﺕﻠﮔﭖ?*: ﮒﺗﺑﮒﭦ۵ﮔﺕﻠﮔﭖ?- **ﮒﻟ۶ﮔ۲?*: ﮔﺍﮔ؟ﮒ؟ﮒ۷ﮒﻟ۶



---



## 8. ﻠ۲ﻠ۸ﻛﺕﻝﭦ۵?

### 8.1 ﮔﮔﺁﻠ۲ﻠ۸ﻟﺁﮒ،ﻛﺕﻝﺙﻟ۶۲ﮔ۹ﮔﺛ



#### P1ﺅﺙﻠ،ﻠ۲ﻠ۸?1. **ﻠ۲ﻠ۸**: ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻟﺁﺁﮔ۴ﮒﺁﺙﻟﺑﻛﺕﮒﺟﻟ۵ﻝﮔ۷۰ﮒﻠﻟ؟ﻝﭨ

   - **ﮒﺛﺎﮒ**: ?- ﮔﭖ۹ﻟﺑﺗﻟ؟۰ﻝ؟ﻟﭖﮔﭦ

   - **ﮔ۵ﻝ**: ?   - **ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ**: ﻟ؟ﺝﻝﺛ؟ﮒﻝﻠﮒﺙﺅﺙﻝﭨﮒﮒ۳ﻝ۶ﮔ۲ﮔﭖﮔﺗ?   - **ﻟﺑ۲ﻛﭨﭨ?*: AIﮒﺓ۴ﻝ۷?

2. **ﻠ۲ﻠ۸**: ﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮔﺙﮔ۴ﮒﺁﺙﻟﺑﮔ۷۰ﮒﮔ۶ﻟﺛﻠ?   - **ﮒﺛﺎﮒ**: ?- ﮒﺛﺎﮒﻛﭦ۳ﮔﮒﺏﻝ

- **ﮔ۵ﻝ**: ?   - **ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ**: ﮒ۳ﮒﺎﮔ؛۰ﮔ۲ﮔﭖﺅﺙﮒ؟ﮔﻛﭦﭦﮒﺓ۴ﮒ؟۰ﮔﺕ

   - **ﻟﺑ۲ﻛﭨﭨ?*: AIﮒﺓ۴ﻝ۷?

### 8.2 ﮒ؟ﮔﺛﻠ۲ﻠ۸ﻛﺕﮒﭦﮒﺁﺗﮔﺗ?

- **ﮔﻟﺛﻝﺙﭦ?*: ﻝﭨﻟ؟۰ﮒ۵ﻝ۴ﻟﺁﻟ۵ﮔﺎﺅﺙﮔﻛﺝﮒﺗﻟ؟

- **ﮔﭘﻠﺑﮒﮒ**: ﻛﺙﮒﮒ؟ﻝﺍﮔﺕﮒﺟﮒﻟﺛ

- **ﻟﭖﮔﭦﻠﮒﭘ**: ﻛﺙﮒﻝ؟ﮔﺏﮔﻝ



### 8.3 ﻝﭦ۵ﮔﮔ۰ﻛﭨﭘ



- **ﮔﮔﺁﻝﭦ۵?*: ﮒﺟﻠ۰ﭨﻛﺛﺟﻝ۷ﮒﺙﮔﭦﮔﺗ?- **ﻟﭖﮔﭦﻝﭦ۵ﮔ**: ﮒﮔﭦﻠ۷ﻝﺛﺎ

- **ﮔﭘﻠﺑﻝﭦ۵ﮔ**: 6ﮒ۷ﮒﮒ؟ﮔ



---



## 9. ﻠ۹ﮔﭘﮔﮒ



### 9.1 ﮒﻟﺛﻠ۹ﮔﭘﮔﮒ



| ﮒﻟﺛ | ﻠ۹ﮔﭘﮔﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |

|------|----------|----------|

| ﻝﺗﮒﺝﮔﺙﻝ۶ﭨﮔ۲?| ﮒﻝ۰؟ﻝﻗ۴90% | ﮒﻟﺛﮔﭖﻟﺁ |

| ﮔ۵ﮒﺟﭖﮔﺙﻝ۶ﭨﮔ۲?| ﮒﻝ۰؟ﻝﻗ۴85% | ﮒﻟﺛﮔﭖﻟﺁ |

| ﻠ۱ﮔﭖﮔﺙﻝ۶ﭨﮔ۲?| ﮒﻝ۰؟ﻝﻗ۴90% | ﮒﻟﺛﮔﭖﻟﺁ |

| ﮒﻟ۵ﻟ۶۵ﮒ | ﮒﭨﭘﻟﺟ?0?| ﮒﻟﺛﮔﭖﻟﺁ |



### 9.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘﮔﮒ



| ﮔﮔ | ﻝ؟ﮔ?| ﻠ۹ﻟﺁﮔﺗﮔﺏ |

|------|--------|----------|

| ﮔ۲ﮔﭖﮒﭨﭘ?| ?0?| ﮔ۶ﻟﺛﮔﭖﻟﺁ |

| ﮔ۲ﮔﭖﮒﻝ۰؟ﻝ | ?0% | ﮒﻟﺛﮔﭖﻟﺁ |

| ﻟﺁﺁﮔ۴?| ?% | ﻝﭨﻟ؟۰ﮒﮔ |

| ﮒﺁﻝ۷?| ?9.9% | ﻝﮔ۶ﻝﭨﻟ؟۰ |



### 9.3 ﻟﺑ۷ﻠﻠ۹ﮔﭘﮔﮒ



| ﮔﮔ | ﻝ؟ﮔ?|

|------|--------|

| ﻛﭨ۲ﻝﻟ۵ﻝ?| ?0% |

| ﮔﮔ۰۲ﮒ؟ﮔﺑ?| 100% |

| APIﻟ۶ﻟ?| 100% |

| ﮒ؟ﮒ۷ﮒﻟ۶ | ﻠﻟﺟ |



---



## 10. ﮒ؟ﮔﺛﻟﺓﺁﻝﭦﺟ?

### 10.1 Phase 1: ﻝﺗﮒﺝﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﺅﺙWeek 1-2?0ﮒﺍﮔﭘ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**?- [ ] ﮒ؟ﻝﺍKSﮔ۲?- [ ] ﮒ؟ﻝﺍPSIﻟ؟۰ﻝ؟

- [ ] ﮒ؟ﻝﺍﻝﺗﮒﺝﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮒ۷

- [ ] ﮒﮒﮔﭖﻟﺁ



**ﻛﭦ۳ﻛﭨ?*?- KSﮔ۲ﻠ۹ﻛﭨ۲?- PSIﻟ؟۰ﻝ؟ﻛﭨ۲ﻝ

- ﻝﺗﮒﺝﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮒ۷ﻛﭨ۲ﻝ

- ﮒﮒﮔﭖﻟﺁﻛﭨ۲ﻝ



### 10.2 Phase 2: ﮔ۵ﮒﺟﭖﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﺅﺙWeek 3?ﮒﺍﮔﭘ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**?- [ ] ﮒ؟ﻝﺍADWINﻝ؟ﮔﺏ

- [ ] ﮒ؟ﻝﺍﮔ۵ﮒﺟﭖﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮒ۷

- [ ] ﮒﮒﮔﭖﻟﺁ



**ﻛﭦ۳ﻛﭨ?*?- ADWINﻝ؟ﮔﺏﻛﭨ۲ﻝ

- ﮔ۵ﮒﺟﭖﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﮒ۷ﻛﭨ۲ﻝ

- ﮒﮒﮔﭖﻟﺁﻛﭨ۲ﻝ



### 10.3 Phase 3: ﻠ۱ﮔﭖﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﺅﺙWeek 4?ﮒﺍﮔﭘ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**?- [ ] ﮒ؟ﻝﺍﻠ۱ﮔﭖﮔﺙﻝ۶ﭨﮔ۲?- [ ] ﮒﮒﮔﭖﻟﺁ



**ﻛﭦ۳ﻛﭨ?*?- ﻠ۱ﮔﭖﮔﺙﻝ۶ﭨﮔ۲ﮔﭖﻛﭨ۲?- ﮒﮒﮔﭖﻟﺁﻛﭨ۲ﻝ



### 10.4 Phase 4: ﮒﻟ۵ﻛﺕﻠﮔﺅﺙWeek 5-6?ﮒﺍﮔﭘ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**?- [ ] ﮒ؟ﻝﺍﮒﻟ۵ﮔﭦﮒﭘ

- [ ] ﻠﮔﮒﺍﻝﮔ۶ﻝﺏﭨ?- [ ] ﻝ،ﺁﮒﺍﻝ،ﺁﮔﭖ?

**ﻛﭦ۳ﻛﭨ?*?- ﮒﻟ۵ﮔﭦﮒﭘﻛﭨ۲ﻝ

- ﻠﮔﻛﭨ۲ﻝ

- ﮔﭖﻟﺁﮔ۴ﮒ



---



**ﮔﮔ۰۲ﻝﮔ؛**: v1.0.0

**ﮔﮒﮔﺑ?*: 2026-04-03

**ﻝﭨﺑﮔ۳?*: AIﮒﺓ۴ﻝ۷?

