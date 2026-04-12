---
module_id: METADATA_ENHANCER_GUIDE
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - METADATA_ENHANCER操作指南
layer: layer_05
standard_type: тиЦтЁиТїЄтЇЌ
applicable_scope: "тЁЃТЋ░ТЇуАуљ?compliance_level: ТГБт╝ЈТаЄтЄє"
parent_document: ../README.md
implementation_status: "ти▓тїТѕ?owner: ТќЄТАБуАуљєтЉ?version: 1.0.0"
tags: ["тиЦтЁиТїЄтЇЌ", "тЁЃТЋ░ТЇ?, "УЄфтіетї?, "Сй┐ућеТЅІтєї"]
---
---



# тЁЃТЋ░ТЇтбът╝║тиЦтЁиСй┐ућеТїЄтЇ?

> **核心职责**: 文档内容说明

> **职责边界**: 

> - ✅ 本文档负责：文档内容说明相关内容

> - ❌ 本文档不负责：其他模块内容



**ТќЄТАБуЅѕТюг**: 1.0.0

**ТюђтљјТЏ┤Тќ?*: 2026-04-02

**ТќЄТАБТЅђТюЅУђ?*: ТќЄТАБуАуљєтЉ?

---



## 1. тиЦтЁиТдѓУ┐░



### 1.1 тиЦтЁиуђС╗?

тЁЃТЋ░ТЇтбът╝║тиЦтЁиућеС║јУЄфтіеТјеТќГтњїУАЦтЁЁТќЄТАБтЁЃТЋ░ТЇ№╝їуАС┐ЮТќЄТАБтЁЃТЋ░ТЇтїТЋ┤ТђДтњїУДёУїЃТђДсђ?

### 1.2 СИ╗УдЂтіЪУЃй



- Рю?УЄфтіеТјеТќГтЁЃТЋ░ТЇ?- Рю?ТЅ╣жЄЈТи╗тіатЁЃТЋ░ТЇ?- Рю?жфїУЂтЁЃТЋ░ТЇтїТЋ┤Тђ?- Рю?ућЪТѕљтбът╝║ТіЦтЉі



---



## 2. т┐ФжђЪт╝ђтД?

### 2.1 тЪ║ТюгСй┐уће



**тбът╝║тЁЃТЋ░ТЇ?*:

```bash

python scripts/metadata_enhancer.py

```



**жфїУЂтЁЃТЋ░ТЇ?*:

```bash

python scripts/metadata_enhancer.py --validate

```



---



## 3. тіЪУЃйУдУДБ



### 3.1 тЁЃТЋ░ТЇТјеТќ?

**ТјеТќГУДётѕЎ**:

- С╗јТќЄС╗ХУитЙёТјеТќГmodule_id

- С╗јТќЄС╗ХтљЇТјеТќГТаЄжбў

- С╗јуЏтйЋу╗ЊТъёТјеТќГтѕєу▒?

**уц║СЙІ**:

```

ТќЄС╗ХУитЙё: docs/02_FACTOR_LIBRARY/01_FACTORS/MOMENTUM_FACTOR.md

ТјеТќГу╗ЊТъю:

  - module_id: MOMENTUM_FACTOR

  - category: 02_FACTOR_LIBRARY

  - title: тіежЄЈтЏатГљ

```



### 3.2 тЁЃТЋ░ТЇжфїУ?

**т┐ЁжюђтГЌТх**:

- owner

- version

- module_id

- created_date

- last_updated



**ТјеУЇљтГЌТх**:

- standard_type

- applicable_scope

- compliance_level

- parent_document



---



## 4. жЁЇуйжђЅжА╣



### 4.1 ТјеТќГУДётѕЎжЁЇуй



```yaml

inference_rules:

  module_id:

    source: "filename"

    pattern: "([A-Z_]+)\\.md"

  

  category:

    source: "directory"

    mapping:

      "01_FRAMEWORK": "ТАєТъХТќЄТАБ"

      "02_FACTOR_LIBRARY": "тЏатГљт║?

```



---



## 5. ТюђСй│тъУи?

### 5.1 Сй┐ућеТеАТЮ┐



**тѕЏт╗║ТќЄТАБТЌХСй┐ућеТеАТЮ?*:

```bash

# Сй┐ућеТќЄТАБТеАТЮ┐

cp docs/09_AUDIT/TEMPLATES/DOCUMENT_TEMPLATE.md new_document.md

```



### 5.2 тџТюЪжфїУЂ



**ТЈТюѕжфїУЂтЁЃТЋ░ТЇтїТЋ┤Тђ?*:

```bash

python scripts/metadata_enhancer.py --validate

```



---



## 6. тЈѓУђЃТќЄТА?

- тЁЃТЋ░ТЇтбът╝║тиЦтЁиТіђТюУДёУїЃ

- ТќЄТАБТеАТЮ┐



---



**ТќЄТАБуіХТђ?*: ТГБт╝ЈТаЄтЄє

**СИІТгАТЏ┤Тќ░**: 2026-07-02

