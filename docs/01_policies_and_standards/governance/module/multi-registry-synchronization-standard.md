---
module_id: GOV-MOD-007
title: ��ǼǱ�ͬ����׼
doc_type: standard
status: active
version: "2.1.1"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-02"
ttl: permanent
summary: "����������Ŀ��������������/ģ��/�ű�/ADR/�ĵ�/Ŀ¼/�Ž�/֪ʶ��Ŀ�ȣ������ͬ�����µĵǼǱ��嵥��ͬ��˳��`catalogs/` ���Զ���¼���� `registry-master-index.yaml` �� `total_registries` Ϊ׼����д����������MRS-001 �����԰� 15 ��Ǽ�Ŀ��������д�������v2.1.1��������ʷ�İ������õġ�24 �š��������Ա� ITIL SACM + AGENTS.md ��6.2��"
tags: [module, governance, registry, synchronization, multi-registry, ssot, artifact-lifecycle]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "��2", why: "frontmatter �ֶκϷ��ԡ������ĵ����� frontmatter �ֶθ�ʽ��ѭ��Լ��"}
  - {target: PS-REG-002, at: "cross_registry_rules", why: "`registry-of-registries.yaml` �е� CR ���򣨿������ֶ��� SSoT �������������׼�����ڵǼǱ�ͬ�������ϵ���ع淶"}
  - {target: PS-REG-005, at: "��2", why: "�ǼǱ�����������`total_registries` ��̬��¼������׼ MRS-001 ����ȫ���ɵǼ�Ŀ�����"}
  - {target: GOV-MOD-001, at: "��8", why: "׼���¼д�롪������ģ��ʱ MRS-001 ������׼���¼ģ��"}
  - {target: GOV-MOD-003, at: "��3", why: "status �ܿ�ö�١���module-registry.yaml �� blueprint.status ֵ��Դ�ڴ�"}
ai_autonomy: ai_modifiable
---

# ��ǼǱ�ͬ����׼

> module_id: GOV-MOD-007 | version: 2.1.1 | status: active | layer: L1

---

## 1. Ŀ���뷶Χ

### 1.1 Ŀ��

**`docs/01_policies_and_standards/_registry/catalogs/*.yaml` ���Զ���¼�嵥**�� [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml) �� **`total_registries`** ΪΨһ��Դ��**����д����**���� `generate_registry_master_index.py` ���һ�����Ϊ׼�����±����� **MRS-001 �Ǽ�Ŀ�����**��15 �๤���򣻺�����·���� `03_modules/*.yaml`����**����**�� `total_registries` ��Ϊһ̸��

| ���� | �ǼǱ��� | ʾ�� |
|------|:---:|------|
| governance_rule | 2 | document-metadata-index.yaml |
| document | 1 | document-metadata-index.yaml��ԭ master-document-inventory.yaml �ѷ����� |
| module | 4 | module-registry.yaml, blueprint-registry.yaml, module-id-registry.yaml, task-card-meta-registry.yaml |
| ai_asset | 4 | ai-autonomy-authority-registry.md, embedding_model_registry.yaml |
| risk | 1 | ai-risk-register.yaml |
| infrastructure | 1 | infrastructure-registry.yaml |
| dependency | 1 | cross-module-dependency-registry.yaml |
| operational | 1 | script-health-registry.yaml |
| knowledge | 1 | knowledge-article-registry.yaml |
| vocabulary | 3 | doc_type / rule_form / status �ܿشʱ� |
| contract | 1 | architecture-contract.yaml |
| field_definition | 1 | frontmatter-field-registry.yaml |
| physical_structure | 1 | directory-registry.yaml |
| quality_gate | 1 | gate-registry.yaml |
| architecture_decision | 1 | adr-status-registry.yaml��**��ɾ��**����ԴǨ���� KB���� KE-governance-adr_registry_migration-000�� |

�޸��κ�һ���ǼǱ�Ĺ����ֶζ���ͬ��������صǼǱ���ᵼ�����ݲ�һ�¡��������� 4 �����ץס 25 ������Ĺ�ͬ�������������ģ��ǼǱ��������ԭ�����������з��ࣩ��

����׼���壺**����/�޸��κ���Ŀ������artifact���󣬱���ͬ��������Щ�ǼǱ������˳��У�鷽ʽ**��

### 1.2 ���η�Χ������׼��ʲô��

- **��������**����������/ģ��/�ű�/ADR/�ĵ�/Ŀ¼/�Ž�/֪ʶ��Ŀ�ȹ����󣬱���д����Щ�ǼǱ�
- **�޸Ĳ���**���޸Ŀ������ֶκ󣬱���ͬ����Щ�ǼǱ�
- ͬ����ԭ����Ҫ�����й���������ͬһ���β�������ɣ�
- ͬ�����У�鲽��
- Υ��ͬ������ĺ���Ͳ�������

### 1.3 ���α߽磨����׼����ʲô��

- ���ǼǱ��ֶεľ��嶨�� �� �Ը��ǼǱ������ `_schema` Ϊ׼
- �������ֶε� SSoT ���� �� �� [registry-of-registries.yaml](../../_registry/catalogs/registry-of-registries.yaml) `cross_registry_rules` Ϊ׼
- �ǼǱ�����嵥 �� �� [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml) Ϊ׼
- AI �������ߵľ�����÷�ʽ �� �� AGENTS.md Ϊ׼
- ���๤����׼������ �� �Զ�Ӧ��׼���׼Ϊ׼��ģ��=GOV-MOD-001������=PS-STD-004��ADR=ADR �������̣�
- �ǼǱ���������Ǩ�ƣ��� module-registry.yaml �� _registry/catalogs/���� �� registry-master-index.yaml migration_plan Ϊ׼

### 1.4 ���÷�Χ

- ��Ŀ `` �������� registry-master-index.yaml �еǼǵĵǼǱ�
- �����������κεǼǱ���д�� registry-master-index.yaml ʱ���ܱ���׼��Ͻ
- ����׼**��������**��`_DO_NOT_USE_old_tree/` �µ��κ��ļ����� AGENTS.md ��2 ��ֹ������

---

## 2. SSoT ����

���ĵ��� ZephyrAlpha ϵͳ��**��ǼǱ�ͬ�������淶**��Ψһ��Դ��SSoT����

**���ĵ�������**��
- 12 �ֹ������� �� 13 ���Ǽ�Ŀ����������ͬ������MRS-001��
- ͬ��ԭ����Լ����MRS-002��
- ͬ����У��Ҫ��MRS-003��
- 6 ����ֹ��Ϊ��MRS-004��

**���ĵ��������ļ�����**����ȡ����ϵ����
- [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml)���г� `total_registries` �� catalogs ��¼�������׼��"���� X ����ôд"������"д�����ű�"
- [registry-of-registries.yaml](../../_registry/catalogs/registry-of-registries.yaml)�������ֶκ� SSoT �����������׼��"��ôͬ��"������"ͬ��ʲô�����ֶ�"
- GOV-MOD-001 ׼���ſأ�����ģ��ʱ���������̡�������׼��׼��ͨ����Ǽ����ݵĲ����淶
- GOV-MOD-003 �������ڲ��ԣ�status ö��ֵ���塪������׼�� status ������ͬ������

**�������ļ��г����뱾��׼��ͻ�Ķ�ǼǱ�ͬ�������Ա��ĵ�Ϊ׼��**

---

## 3. �ܿ�ö�ٶ���

���ĵ�������������ܿ�ö�١�����ö��ֵ�� SSoT �������ļ��У�
- �����ֶμ��� SSoT ���� �� [registry-of-registries.yaml](../../_registry/catalogs/registry-of-registries.yaml) `cross_registry_rules`
- `status` 8 �׶�ö��ֵ �� GOV-MOD-003 ��3
- `priority` �Ϸ�ֵ��P0/P1/P2/P3�� �� module-registry.yaml `_schema.priority_values`
- `layer` �Ϸ�ֵ��L00~L13�� �� module-registry.yaml `_schema.layer_values`
- `doc_type` 17 �ֺϷ�ֵ �� REG-VOC-001
- `rule_form` 6 �ֺϷ�ֵ �� REG-VOC-002

---

## 4. ������ע���

�����ļ�ֱ���������ĵ���������׼������ʱ����ͬ�����£�

| ������ | �ļ� | Tier | �������� |
|--------|------|:---:|---------|
| check_registry_consistency.py | `scripts/governance/` | 1 | ��7 У�鲽�衪��У��ű���ִ���������� MRS-003 |
| run_all.py | `scripts/governance/` | 2 | ��ƽű����š����轫 check_registry_consistency.py ���� 40 ������ |
| document-metadata-index.yaml | `_registry/catalogs/` | 1 | MRS-001 �����С�������/�޸Ĺ����ĵ�ʱ�ĵǼ�Ҫ�� |
| document-metadata-index.yaml��ԭ master-document-inventory.yaml �ѷ����� | `_registry/catalogs/` | 1 | MRS-001 �ĵ��С��������κ��ĵ�ʱ����Ǽ� |
| module-registry.yaml | `03_modules/` | 1 | MRS-001 ģ���С���ģ������ĵǼ�Ҫ�� |
| blueprint-registry.yaml | `03_modules/` | 1 | MRS-001 ģ���� |
| script-health-registry.yaml | `_registry/catalogs/` | 1 | MRS-001 �ű��� |
| adr-status-registry.yaml��**��ɾ��**�� | `_registry/catalogs/` | 1 | MRS-001 ADR �У�ռλ���ˣ���Ծ���߲��ڴ˱�����ά���� |
| directory-registry.yaml | `_registry/catalogs/` | 1 | MRS-001 Ŀ¼�� |
| gate-registry.yaml | `_registry/catalogs/` | 2 | MRS-001 �Ž��� |
| knowledge-article-registry.yaml | `_registry/catalogs/` | 2 | MRS-001 ֪ʶ��Ŀ�� |

---

## 5. �������� �� ���Ĳ�������

### 5.1 MRS-001������-�ǼǾ���

**����**������Ŀִ�����²���ʱ��MUST ͬ�����¾����д� ? �ĵǼǱ���޸ĵ��ֶ�ֵ MUST �� SSoT Դһ�¡�

**�ǼǱ�����д����**��

| ��д | ȫ�� | ·�� |
|------|------|------|
| GOV-RULES | document-metadata-index.yaml | `_registry/catalogs/` |
| DOC-INV | document-metadata-index.yaml��ԭ master-document-inventory.yaml �ѷ����� | `_registry/catalogs/` |
| MOD-ID | module-id-registry.yaml | `02_enterprise_architecture/.../architecture-model/` |
| MODULE | module-registry.yaml | `03_modules/` |
| BPR | blueprint-registry.yaml | `03_modules/` |
| TASK-META | task-card-meta-registry.yaml | `_registry/catalogs/` |
| SCRIPT | script-health-registry.yaml | `_registry/catalogs/` |
| ADR | adr-status-registry.yaml��**��ɾ��**�� | `_registry/catalogs/` |
| KMS | knowledge-article-registry.yaml | `_registry/catalogs/` |
| DIR | directory-registry.yaml | `_registry/catalogs/` |
| GATE | gate-registry.yaml | `_registry/catalogs/` |
| FIELD | frontmatter-field-registry.yaml | `_registry/catalogs/` |
| AI-AUTH | ai-autonomy-authority-registry.md | `governance/ai/` |
| INFRA | infrastructure-registry.yaml | `_registry/catalogs/` |

**���� �� �ǼǱ����**��

| ���� | GOV-RULES | DOC-INV | MOD-ID | MODULE | BPR | TASK-META | SCRIPT | ADR | KMS | DIR | GATE | FIELD | AI-AUTH | ���� |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|------|
| **�����������** | ? | ? | ? | �� | �� | �� | �� | �� | �� | �� | �� | �� | �� | Ŀ¼ index.md |
| **����ģ��** | �� | ? | ? | ? | ? | �� | �� | �� | �� | ? | �� | �� | ? | �ϼ��� index.md |
| **�����ű�** | �� | ? | �� | �� | �� | �� | ? | �� | �� | �� | �� | �� | �� | �� |
| **���� ADR** | �� | ? | �� | �� | �� | �� | �� | ? | �� | �� | �� | �� | �� | �� |
| **����֪ʶ��Ŀ** | �� | ? | �� | �� | �� | �� | �� | �� | ? | �� | �� | �� | �� | �� |
| **������Ŀ¼** | �� | ? | �� | �� | �� | �� | �� | �� | �� | ? | �� | �� | �� | index.md |
| **�����Ž�** | �� | ? | �� | �� | �� | �� | �� | �� | �� | �� | ? | �� | �� | �� |
| **��������ϵͳ** | �� | ? | �� | �� | �� | ? | �� | �� | �� | �� | �� | �� | �� | �� |
| **���� frontmatter �ֶ�** | �� | �� | �� | �� | �� | �� | �� | �� | �� | �� | �� | ? | �� | PS-STD-001 |
| **�޸Ĺ����ֶ�** | �� | �� | �� | ? | ? | �� | �� | �� | �� | �� | �� | �� | �� | ������ͼ.md |
| **ģ��� version** | �� | �� | �� | ? | ? | �� | �� | �� | �� | �� | �� | �� | �� | ������ͼ.md |
| **ģ��� status** | �� | �� | �� | ? | ? | �� | �� | �� | �� | �� | �� | �� | �� | ������ͼ.md |
| **ģ��鵵/����** | �� | �� | �� | ? | ? | �� | �� | �� | �� | �� | �� | �� | �� | delivery/index.md |
| **����������ʩ���** | �� | ? | �� | �� | �� | �� | �� | �� | �� | ? | �� | �� | �� | INFRA |

> **����ͬ���ĵǼǱ����**��vocabulary���ܿشʱ����ֻ����ö�٣����ǼǾ��幤������contract����֤��Լ����ֻ������֤���򣩡�dependency��ģ������������� MODULE �ֶ��Ƶ����� CR-004 ע����risk�����յǼǡ���������;���� OPS-VC �������̵Ǽǣ����ڱ���׼�Զ�ͬ����Χ��

### 5.2 ���������͹�����ͨ�ò���ģ��

���۴���ʲô���͵Ĺ�������ѭͳһ���裺

1. **�� MRS-001 ����**��ȷ����Щ�ǼǱ��� ?
2. **���������ļ�**��д��ʵ������ + ���� PS-STD-001 �� frontmatter
3. **д�����д� ? �ĵǼǱ�**����ͬһ�����������
4. **���¹���Ŀ¼ index.md**�������������"����"�б�ע
5. **�������У��ű�**������ MRS-003��

### 5.3 ����ģ��ʱ���������裨��ӳ�����

ģ���Ǻ�����ǼǱ�Ĺ������ͣ���Ϊ�ο�ģ�壺

1. **���� module_id**���� MOD-ID �ǼǱ��ȡ���һ�� ID ����
2. **��������Ŀ¼���ļ�**��`{layer_dir}/{module_name}/` + `index.md` + `blueprint.md` + `delivery/index.md`
3. **�Ǽ� MODULE**��module-registry.yaml�������� `modules[]` ��Ŀ
4. **�Ǽ� BPR**��blueprint-registry.yaml�������� `blueprints[]` ��Ŀ
5. **�Ǽ� DOC-INV**�������ĵ���Ŀ
6. **�Ǽ� MOD-ID**��ע���� id
7. **�Ǽ� DIR**��ע����Ŀ¼
8. **�Ǽ� AI-AUTH**������ AI ����Ȩ��
9. **�����ϼ��� index.md**�����ģ����
10. **����У��**��`check_registry_consistency.py` + `check_frontmatter_metadata.py`

### 5.4 MRS-002��ͬ��ԭ����

**����**�����й����ǼǱ���޸� MUST ��ͬһ���β�������ɡ�

- ��ֹ�ȸ� A �ٸ� B���ֿ�����������������һ�� SearchReplace/Write ���θ�������Ŀ���ļ�
- ���ĳ�������ļ���ǰ���ڱ༭�������ڣ�MUST �� Read ���ļ��ټ���ͬ�����޸�
- ԭ���ԶԱ� AGENTS.md ��6.2

**��׻�**�����������ĵ�ʱ��document-metadata-index.yaml + module-id-registry.yaml �����ǼǱ����һ����£�ԭ master-document-inventory.yaml �ѷ����� document-metadata-index.yaml ȡ���������ܽ���дһ�����첹һ��������֪��Ϊʲô 4 �����ץס�� 25 �������ˡ���ÿ�ζ���"������Ҫ������벻����ͬ����"��

### 5.5 MRS-003��ͬ����У��

**����**���κδ��� MRS-001 ������ ? ��ǵ��޸���ɺ�MUST �����������У�飺

| У�� | ���� | ��ʱ���� |
|------|------|---------|
| `check_registry_consistency.py` | ��ǼǱ�����ֶ�һ���ԣ�CR-001~006�� | �κδ��� module-registry.yaml / blueprint-registry.yaml / ���� blueprint.md �Ĳ����� |
| `check_frontmatter_metadata.py` | frontmatter �ֶκϷ��� | �����κ��ĵ��� |
| `check_architecture_gates.py` | ADR/ģ��/�ܹ�һ���� | ����/�޸� ADR ��ģ��� |
| `validate_directory_registry.py` | ����Ŀ¼ vs �ǼǱ�Ư�� | ������Ŀ¼�� |

- ���У��ű������ã��� Python �������⣩��MUST �ֶ��������� SSoT ������֤
- �κ� FAIL ������ commit ǰ�޸�

---

## 6. ��ֹ��Ϊ

### MRS-004����ֹ��Ϊ�嵥

������Ϊ��**��ȷ��ֹ**��Υ������Ϊͬ��Υ�棺

| # | ��ֹ��Ϊ | ʾ�� | ��� |
|---|---------|------|------|
| 1 | **�����������Ǽ�**�������������ĵ�/�ű�/����/ADR����û��д���Ӧ�ĵǼǱ� | ������ GOV-MOD-007 ��δд�� document-metadata-index.yaml | �� AI session �����ǼǱ�ʱ�ù������ɼ�����Υ�� Zero-Memory Restart ��׼ |
| 2 | **ֻ�������ļ����õǼǱ�**�������� frontmatter �Ĺ����ֶΣ���δͬ���κεǼǱ� | ���� blueprint.md �� version��module-registry.yaml �� BPR ���Ǿ�ֵ | CR-001 FAIL |
| 3 | **ֻ�ĵǼǱ���������ļ�**�������˵ǼǱ�Ĺ����ֶΣ����� frontmatter ��ͬ�� | ���� module-registry �� status��blueprint.md frontmatter δ�� | �����ļ���ǼǱ���롪�������ļ��� SSoT���Ǽ�ƫ������û� |
| 4 | **���� A �ǼǱ���� B �ǼǱ�**���������ǼǱ���ͬһ�������ֶΣ�ֻ����һ�� | ���� module-registry �� version��BPR ���Ǿ�ֵ | CR-001 FAIL����AI ����ì�ܰ汾 |
| 5 | **SearchReplace ģ�岻Ψһ������ƥ��**����������¼������ͬ�ֶ�ֵ���滻���д���Ŀ�� | v1.0.0+AI-GLM-5.1 ͬʱ������ MOD-INF-001 �� MOD-INF-003��������׼�� root cause | SearchReplace ֻ�滻��һ��ƥ�䡪����Ҫ���컯��ʹ�ø�Ψһ�������� |
| 6 | **�����ǼǱ��������Ǽǵ� registry-master-index.yaml**����������һ�� YAML �ǼǱ������������֪�� | ������ deploy-registry.yaml��δд�� registry-master-index | MRS-001 ����ȱʧ�ñ����Υ�� ��1.4"�������ܹ�Ͻ" |

---

## 7. ���ͬ������

����׼ `stability: evolving`������������ͽ�ֹ��Ϊ���� Phase �仯��

| ������� | Ӱ�췶Χ | ͬ������ | ʱ�� |
|---------|---------|---------|------|
| �����ǼǱ��д�� registry-master-index.yaml�� | MRS-001 ���������� | ��չ������ + ������Ӧ������ | ͬ commit |
| �����������ͣ��� deploy-artifact�� | MRS-001 ���������� | ���������� + ���� ��15 AI �嵥 | ͬ commit |
| �޸� MRS-001 ����ӳ�� | Tier 1 ������ | ���� check_registry_consistency.py ���ֶ�ƥ���߼� | ͬ commit |
| ������ֹ��Ϊ | MRS-004 ��ŵ��� | �������������� | ͬ commit |
| frontmatter �������summary/tags�� | �� | ����ͬ�� | �� |

---

## 8. �޸�����

����׼ `ai_autonomy: ai_modifiable`����AI �������޸ģ��������·ּ�Լ����

| ���� | �����Χ | ������ | Ҫ�� |
|:---:|---------|--------|------|
| L0 | ����֡�����Ż�����ʽ���� | AI ���� | Session Log ��¼ |
| L1 | MRS-001 ����������/ɾ�������� | AI �ɽ��飬Owner ȷ�� | ����� registry-master-index.yaml ��֤�����ǼǱ���ע�� |
| L2 | �޸� MRS-002~005 ������ | Owner ���� | �漰�������ɡ����� Owner ȷ���¹������� |
| L3 | �����ǼǱ�� MRS-001 ���� / ������������ | Owner ���� | ����ͬʱ���� registry-master-index.yaml + registry-of-registries.yaml |

---

## 9. ��׼�����ù淶

### 9.1 �淶�����ã�Normative��

| �����ļ� | �� | ��ɫ |
|---------|---|------|
| AGENTS.md | ��6.2 | ԭ������ģʽ��������ͬ������������һ��������� |
| registry-of-registries.yaml | cross_registry_rules | �����ֶζ���� SSoT �����������׼�� CR �����ʩ��������ط��� |
| registry-master-index.yaml | ��2 | �ǼǱ�����嵥����MRS-001 �����оݴ����� |
| PS-STD-001 | ��2 | frontmatter �ֶκϷ��ԡ������ļ����� frontmatter ��ʽ��ѭ��Լ�� |

### 9.2 ��Ϣ�����ã�Informative��

| �����ļ� | �� | ��ɫ |
|---------|---|------|
| GOV-MOD-001 | ȫ�� | ģ��׼���ſء�������ģ���ǰ���������� |
| GOV-MOD-003 | ��3 | status ö��ֵ����module-registry.yaml �� blueprint.status ֵ��Դ |
| check_registry_consistency.py | ȫ�� | У��ű�����MRS-003 ��ִ��Ŀ�� |
| PS-STD-004 | ȫ�� | ��������׼����������������ǰ�÷���Ҫ�� |

---

## 10. ��������

�����׼�����߲㼶�������ļ�ȡ����

1. **����Ӱ��**��ȫ��Ŀ���� `MRS-001|MRS-002|MRS-003|MRS-004`����ȷ���������ö���Ǩ��·��
2. **֪ͨ��**��30 ����ǰ֪ͨȫ�������ߣ�Session Log + ADR��
3. **�������**��`status: deprecated`��`superseded_by` ָ������ļ�
4. **������**������ 90 �챣����ļ����ڼ����������Ǩ��
5. **����**��90 �쵽�ں�������δǨ�� �� Owner ����׼���ڣ������ 90 �죩�������� Session Log ��¼ԭ��
6. **�鵵**������������ȫ��������Ǩ�� �� `status: archived`

---

## 11. �������

�Ա� ISO 11179 ��6.2 �������Ҫ��

| �������� | ������� |
|---------|---------|
| �����ǼǱ��registry-master-index.yaml ������Ŀ�� | MRS-001 �����Ƿ���Ҫ������ |
| �����������ͣ���Ŀ�г����µĿɴ���ʵ�壩 | MRS-001 �����Ƿ���Ҫ������ |
| Phase �߽磨scaffold��1, 1��2...�� | ���������Ƿ��Ը��ǵ�ǰ�������� |
| check_registry_consistency.py �ش��޸� | MRS-003 У�鲽�������Ƿ�׼ȷ |
| ���Ƶ�ʣ�ÿ 6 ���� | ȫ����� |

---

## 12. �쳣�������

**Ĭ��**��MRS-001~004 �����й�������ͬ��Լ����

**����ͨ��**��

| ���ⳡ�� | �������� | Լ�� |
|---------|---------|------|
| scaffold ԭ�Ϳ��ٵ��� | ��ʱ���� MRS-003 У�鲽�� | Owner ���������� scaffold��ÿ�λ��ⲻ���� 3 �� |
| �ǼǱ�ṹ�ع� | ����ǼǱ���ʱ��һ�� | Session Log ��¼��һ���嵥 + �޸�ʱ�ޣ������� 48h�� |
| ���ڲ��ļ��������ߵĲݸ壩 | ���� DOC-INV������������Ǽ� | �� DOC-INV ��ע�ֶα�ע `internal_draft` |

---

## 13. �� PS-STD-001 ���ֶβ��ظ�����

����׼�������µ� frontmatter �ֶΡ����� frontmatter �ֶζ����� PS-STD-001 Ϊ׼��

---

## 14. ���׼�ֶν�������

����׼��������׼�����ֶΡ������ֶε� SSoT ������ registry-of-registries.yaml `cross_registry_rules[].ssoT` Ϊ׼��

---

## 15. AI ������������

> �Ա� Anthropic CLAUDE.md����ֱ���� AI ˵����ν�����ִ�б��ĵ���

### 15.1 AI ��ֱ��ִ�еĹ���

- **MRS-001 ��������**��12 �� �� 14 �е���ֵ��������ȷ������ X �����д��Щ�ǼǱ�
- **MRS-002 ԭ����**������ ? Ŀ�������ͬһ�� SearchReplace/Write �����
- **MRS-003 У��**���޸���ɺ��Զ�ִ�ж�Ӧ��У��ű�
- **MRS-004 ��ֹ��Ϊ**��#1~#6 ÿ���д��������ͺ��

### 15.2 �������жϵĹ���

- �µǼǱ�����루L3 ���޸ģ��� Owner ������
- ���ⳡ������������ Owner ȷ�ϣ�

### 15.3 ��С�ض�·����ȫ�� AI session��

1. ��1.1 �� ֪���� 15 ������ĵǼǱ�ϵͳ
2. ��5.1 MRS-001 ���� �� �������� X �� ����д Y��Z
3. ��5.4 MRS-002 ԭ���� �� ���� ? ��ͬ�����
4. ��5.5 MRS-003 У�� �� ��������У��
5. ��6 MRS-004 �� ֪�� 6 �ֳ�������ģʽ

### 15.4 Token Ԥ��

| ��Ŀ | ֵ |
|------|---|
| ȫ�� Token | ~3000 |
| ����·����Ŀ�� + ���� + У�� + ��ֹ��Ϊ�� | ~1200 |

### 15.5 AI ִ���嵥

�� AI ����κδ���/�޸Ĳ���ʱ��

- [ ] ȷ���������ͣ�����/ģ��/�ű�/ADR/�ĵ�/Ŀ¼/�Ž�/֪ʶ/�ֶΡ���
- [ ] �� ��5.1 MRS-001 ���� �� �ҳ����� ? �ĵǼǱ���
- [ ] ͬһ�������������� ? Ŀ��
- [ ] ���� MRS-003 ָ����У��ű�
- [ ] ȷ������У�� PASS
- [ ] Session Log ��¼ͬ������

---

## 16. �������Լ��嵥

- [ ] ��1.1 Ŀ�ģ�`total_registries` �� MRS-001 15 ��Ǽ�Ŀ��Ŀھ������֣���д��������
- [ ] ��2 SSoT ������������ϵ���� registry-master-index.yaml + registry-of-registries.yaml + GOV-MOD-001/003
- [ ] ��5.1 MRS-001���������󸲸� 12 �ֲ��� �� 14 ���Ǽ�Ŀ�꣬��ע�ų��ķ���
- [ ] ��5.3 ����ģ�鲽�裺10 ���������̣���ӳ�����
- [ ] ��6 MRS-004��6 ����ֹ��Ϊ������ #5 SearchReplace ��ƥ�䡢#6 �µǼǱ�δע�ᣩ
- [ ] ��15 AI ����������������С·�� + Token + ִ���嵥

---

## 17. �����¼

| ���� | �汾 | ���˵�� |
|------|------|---------|
| 2026-05-06 | 2.1.1 | ���� `registry-master-index.yaml`���Ƴ����õġ�24 �š���������Ϊ `total_registries` ��Դ + MRS-001 ����˵�����Լ��嵥ͬ���� |
| 2026-05-02 | 2.0.0 | **�ش���չ**��MRS-001 ��������� 3 �У���ģ��ǼǱ����չ�� 14 �У����� registry-master-index.yaml ����ȫ���ɵǼǷ��ࣩ������ 8 �ֲ������ͣ���������/�ű�/ADR/֪ʶ/Ŀ¼/�Ž�/����/�ֶΣ���MRS-004 ��ֹ��Ϊ�� 4 ����չ�� 6 �������� SearchReplace ��ƥ�� + �µǼǱ��ע�ᣩ��depends_on ���� registry-master-index.yaml��Token Ԥ����£�2000��3000���� |
| 2026-05-02 | 1.0.0 | ��ʼ�汾�������� MRS-001~004 �������Ĺ��򣬽�����ģ��ǼǱ��module-registry.yaml + blueprint-registry.yaml + ���� blueprint.md�� |
