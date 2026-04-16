#!/usr/bin/env python3
"""
文档缺陷防护 pre-commit 钩子

实现 DOCUMENT_DEFECT_PREVENTION_STANDARD 中定义的 6 类检查：
  D-01 双 YAML frontmatter
  D-02 BOM 字符污染
  D-03 无效内链（增量模式）
  D-04 重复 module_id
  D-05 编码损坏（乱码）
  D-06 目录映射缺失

用法:
  # Pre-commit 模式（检查暂存文件）
  python scripts/doc_guard_pre_commit.py --check single --file path/to/file.md
  python scripts/doc_guard_pre_commit.py --check staged

  # 全量扫描模式（CI/CD）
  python scripts/doc_guard_pre_commit.py --check full

  # 单项扫描
  python scripts/doc_guard_pre_commit.py --scan-bom
  python scripts/doc_guard_pre_commit.py --scan-double-yaml
  python scripts/doc_guard_pre_commit.py --scan-encoding
  python scripts/doc_guard_pre_commit.py --scan-module-id
  python scripts/doc_guard_pre_commit.py --scan-links

退出码:
  0 - 全部通过
  1 - 阻止提交的缺陷（D-01, D-02, D-04, D-05）
  2 - 警告（D-03 增量, D-06）
"""

import argparse
import io
import re
import sys
import yaml
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple, Dict, Optional

# Windows 控制台 UTF-8 兼容
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 项目根目录（scripts/hooks/ → 仓库根需上溯两级）
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = PROJECT_ROOT / "docs"

# 非 ASCII 乱码检测模式：连续的非 ASCII 字符中混入替换字符或常见乱码模式
MOJIBAKE_PATTERNS = [
    re.compile(r'[\ufffd\u00ef\u00bb\u00bf]'),  # 替换字符、BOM 残留
    re.compile(r'[\u00c0-\u00ff]{3,}'),  # 连续 Latin Extended 字符（常见 UTF-8 被误读为 Latin-1）
    re.compile(r'Ã[ÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞß]'),  # UTF-8 字节被双重编码
]


class DocGuardChecker:
    """文档缺陷防护检查器"""

    def __init__(self, docs_root: Path = DOCS_ROOT):
        self.docs_root = docs_root
        self.blocking_errors: List[Dict] = []  # 退出码 1
        self.warnings: List[Dict] = []  # 退出码 2

    def reset(self):
        self.blocking_errors = []
        self.warnings = []

    # ─── D-01: 双 YAML frontmatter ────────────────────────────────

    def check_double_yaml(self, file_path: Path) -> Optional[Dict]:
        """检查文件是否包含双 YAML frontmatter

        检测逻辑：在第一个 frontmatter 块关闭后，紧接的下一个 --- 块
        如果包含 YAML 键值对（key: value），则判定为双 frontmatter。
        这避免了将 Markdown 表格分隔线（|---|）和水平线（---）误判。
        """
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except (UnicodeDecodeError, OSError):
            return None

        # 匹配文件开头的第一个 frontmatter 块
        first_fm = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not first_fm:
            return None

        # 在第一个 frontmatter 之后，查找第二个 --- 块
        after_first = content[first_fm.end():]
        # 跳过空行、换行符和可能的BOM字符
        after_first_stripped = after_first.lstrip('\n\r\ufeff')

        # 检查是否以 --- 开头（第二个 frontmatter 块的开始）
        second_fm = re.match(r'^---\s*\n(.*?)\n---\s*\n', after_first_stripped, re.DOTALL)
        if not second_fm:
            return None

        # 验证第二个块是否包含 YAML 键值对
        second_yaml_str = second_fm.group(1).strip()
        if not second_yaml_str:
            return None

        # 检查是否包含至少一个 YAML 键值对（key: value）
        yaml_kv_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*:', re.MULTILINE)
        if yaml_kv_pattern.search(second_yaml_str):
            second_fm_line = content[:first_fm.end()].count('\n') + after_first[:len(after_first) - len(after_first_stripped)].count('\n') + 1
            return {
                'type': 'D-01',
                'file': str(file_path.relative_to(self.docs_root.parent)),
                'detail': f'发现双 YAML frontmatter（第二个块含 YAML 键值对）',
                'line': second_fm_line
            }
        return None

    # ─── D-02: BOM 字符污染 ────────────────────────────────────────

    def check_bom(self, file_path: Path) -> Optional[Dict]:
        """检查文件是否包含 UTF-8 BOM"""
        try:
            with open(file_path, 'rb') as f:
                first_bytes = f.read(3)
        except OSError:
            return None

        if first_bytes == b'\xef\xbb\xbf':
            return {
                'type': 'D-02',
                'file': str(file_path.relative_to(self.docs_root.parent)),
                'detail': '文件包含 UTF-8 BOM 字符 (\\xEF\\xBB\\xBF)',
                'line': 1
            }
        return None

    # ─── D-03: 无效内链（增量模式）────────────────────────────────

    def check_internal_links(self, file_path: Path) -> List[Dict]:
        """检查文件中的 Markdown 内链目标是否存在"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, OSError):
            return []

        # 提取 Markdown 链接: [text](url)
        link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
        results = []

        for match in link_pattern.finditer(content):
            text = match.group(1)
            url = match.group(2)

            # 跳过外部链接、锚点、图片
            if url.startswith(('http://', 'https://', '#', 'mailto:', 'ftp://')):
                continue
            if url.startswith('data:'):
                continue

            # 去除锚点
            path_part = url.split('#')[0]
            if not path_part:
                continue

            # 解析相对路径
            try:
                # 限制路径长度（Windows 兼容）
                if len(str(file_path.parent / path_part)) > 240:
                    continue

                target = (file_path.parent / path_part).resolve()
                docs_root_resolved = self.docs_root.resolve()

                if not target.exists():
                    # 检查是否在归档区（归档区警告而非阻止）
                    rel_path = str(file_path.relative_to(self.docs_root))
                    is_archive = rel_path.startswith(('06_ARCHIVE/', '09_ARCHIVE/'))

                    results.append({
                        'type': 'D-03',
                        'file': str(file_path.relative_to(self.docs_root.parent)),
                        'detail': f'无效内链: [{text}]({url})',
                        'line': content[:match.start()].count('\n') + 1,
                        'is_archive': is_archive
                    })
            except (ValueError, OSError):
                continue

        return results

    # ─── D-04: 重复 module_id ──────────────────────────────────────

    # 通用文件名 ID 豁免集合（与 dedupe_module_id_frontmatter.py 口径对齐）
    # 这些 ID 是文件名派生的通用 ID，项目治理已接受其存在
    GENERIC_MODULE_IDS = {'INDEX', 'README', 'SITEMAP', 'CHANGELOG', 'LICENSE'}

    # 归档区路径前缀（归档区 overlap 文件与活跃区共享 module_id 是已知且可接受的）
    ARCHIVE_PREFIXES = ('06_ARCHIVE', '09_ARCHIVE')

    def check_module_id_uniqueness(self, file_paths: List[Path]) -> List[Dict]:
        """检查一组文件中首道 frontmatter 的 module_id 是否唯一

        与官方 dedupe_module_id_frontmatter.py 口径对齐：
        跳过通用文件名 ID（INDEX/README/SITEMAP 等），
        仅报告非通用 ID 的跨文件重复。
        """
        module_ids = defaultdict(list)

        for fp in file_paths:
            # 跳过归档区文件（与官方 dedupe_module_id_frontmatter.py 口径对齐）
            try:
                rel = str(fp.relative_to(self.docs_root))
                if any(rel.startswith(p) for p in self.ARCHIVE_PREFIXES):
                    continue
            except ValueError:
                continue

            try:
                with open(fp, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
            except (UnicodeDecodeError, OSError):
                continue

            # 仅解析第一个 --- 块
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not match:
                continue

            try:
                metadata = yaml.safe_load(match.group(1))
                if metadata and isinstance(metadata, dict):
                    mid = metadata.get('module_id')
                    if mid and mid not in self.GENERIC_MODULE_IDS:
                        module_ids[mid].append(fp)
            except yaml.YAMLError:
                continue

        results = []
        for mid, files in module_ids.items():
            if len(files) > 1:
                file_list = ', '.join(
                    str(f.relative_to(self.docs_root.parent)) for f in files
                )
                results.append({
                    'type': 'D-04',
                    'file': file_list,
                    'detail': f'重复 module_id: {mid}（{len(files)} 个文件）',
                    'line': 0
                })
        return results

    # ─── D-05: 编码损坏（乱码）────────────────────────────────────

    def check_encoding(self, file_path: Path) -> Optional[Dict]:
        """检查文件是否存在编码损坏（乱码字符）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return {
                'type': 'D-05',
                'file': str(file_path.relative_to(self.docs_root.parent)),
                'detail': '文件无法以 UTF-8 解码',
                'line': 1
            }
        except OSError:
            return None

        # 检查乱码模式
        for pattern in MOJIBAKE_PATTERNS:
            match = pattern.search(content)
            if match:
                line_num = content[:match.start()].count('\n') + 1
                return {
                    'type': 'D-05',
                    'file': str(file_path.relative_to(self.docs_root.parent)),
                    'detail': f'检测到乱码字符: {repr(match.group())}',
                    'line': line_num
                }
        return None

    # ─── D-06: 目录映射缺失 ────────────────────────────────────────

    def check_sitemap_sync(self, file_path: Path) -> Optional[Dict]:
        """检查新建目录是否在 SITEMAP.md 中有映射"""
        # 仅检查 INDEX.md 文件（新目录的标志）
        if file_path.name != 'INDEX.md':
            return None

        sitemap_path = self.docs_root / 'SITEMAP.md'
        if not sitemap_path.exists():
            return None

        try:
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                sitemap_content = f.read()
        except (UnicodeDecodeError, OSError):
            return None

        # 获取文件所在目录名
        parent_dir = file_path.parent
        dir_name = parent_dir.name

        # 检查目录名是否出现在 SITEMAP 中
        if dir_name not in sitemap_content:
            return {
                'type': 'D-06',
                'file': str(file_path.relative_to(self.docs_root.parent)),
                'detail': f'目录 {dir_name}/ 未在 SITEMAP.md 中映射',
                'line': 0
            }
        return None

    # ─── C-10: 文件命名规范检查 ─────────────────────────────────────

    @staticmethod
    def _is_git_tracked(file_path: Path) -> bool:
        """检查文件是否已被 git 追踪（已存在于历史中）。
        用于祖父条款：已追踪的大写文件免于新规阻断。
        """
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'ls-files', '--error-unmatch', str(file_path)],
                capture_output=True, cwd=str(PROJECT_ROOT)
            )
            return result.returncode == 0
        except Exception:
            return True  # 查询失败时保守放行

    def check_naming_single(self, file_path: Path) -> bool:
        """检查单个文件的命名规范，返回是否有阻断错误。

        单轨标准（自 2026-04-16 起）：
          唯一合法格式 → 全小写 kebab/snake：^[a-z0-9][a-z0-9_-]*\\.md$
          例：construction-plan-l01-data-processing.md
              doc-naming-standard.md

        祖父条款（自动豁免，无需手动维护列表）：
          1. 固定名（永久合法）：INDEX.md / README.md / AGENTS.md / CHANGELOG.md 等
          2. 已被 git 追踪的大写文件：视为历史遗留，警告但不阻断
             → 在 Pipeline A/B 文件消除波次中逐步迁移至小写
          3. 特殊命名模式（显式设计约定）：
             - KE-NNN-slug.md（知识条目）
             - DR-TYPE-YYYYMMDD-NNN.md（决策记录）
             - session-YYYYMMDD-*.md（Session Log）

        硬阻断（exit 1，提交失败）：
          - 中文字符
          - 空格
          - 特殊字符（@#$%&!）
          - 版本号后缀（-v2, _v3, -round2）
          - 【新建】大写 .md 文件且不在 git 追踪中（单轨标准强制）
        """
        import re

        # ── 固定名豁免（永久合法，不检查格式）──────────────────────────
        FIXED_NAMES = {
            'README.md', 'INDEX.md', 'SITEMAP.md', 'AGENTS.md',
            'CHANGELOG.md', 'CONTRIBUTING.md', 'SECURITY.md', 'LICENSE',
        }
        filename = file_path.name
        if filename in FIXED_NAMES:
            return False

        # ── 硬阻断检查 1：中文字符 ──────────────────────────────────────
        if re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]', filename):
            self._report_naming_error(file_path, "包含中文字符", "请使用全小写英文命名，如 data-source-plan.md")
            return True

        # ── 硬阻断检查 2：空格 ──────────────────────────────────────────
        if ' ' in filename:
            self._report_naming_error(file_path, "文件名包含空格", "请用连字符 - 替代，如 data-source-plan.md")
            return True

        # ── 硬阻断检查 3：特殊字符 ────────────────────────────────────
        if re.search(r'[@#$%&!]', filename):
            self._report_naming_error(file_path, "包含特殊字符 (@#$%&!)", "请移除特殊字符")
            return True

        # ── 硬阻断检查 4：版本号后缀 ──────────────────────────────────
        if re.search(r'[-_](v\d+|round\d+|r\d+)\.(md|yaml|yml|json|py)$', filename, re.IGNORECASE):
            self._report_naming_error(file_path, "文件名含版本号后缀（如 -v2, _v3）", "版本历史用 git log 追踪，不要在文件名中加版本号")
            return True

        # ── 格式合规检查（.md 文件专属）──────────────────────────────
        if not filename.endswith('.md'):
            return False

        lowercase_pattern = re.compile(r'^[a-z0-9][a-z0-9_-]*\.md$')
        ke_pattern = re.compile(r'^KE-\d{3}-[a-z0-9-]+\.md$')
        dr_pattern = re.compile(r'^DR-[A-Z]+-\d{8}-\d{3}\.md$')
        session_pattern = re.compile(r'^session-\d{8}.*\.md$')

        # 标准合规：小写 kebab/snake 或特殊设计模式
        if any([
            lowercase_pattern.match(filename),
            ke_pattern.match(filename),
            dr_pattern.match(filename),
            session_pattern.match(filename),
        ]):
            return False  # ✅ 合规

        # ── 硬阻断检查 5：新建大写文件（单轨标准核心约束）────────────
        has_uppercase = re.search(r'[A-Z]', filename)
        if has_uppercase:
            if self._is_git_tracked(file_path):
                # 历史遗留文件：警告但不阻断（祖父条款）
                try:
                    rel_path = file_path.relative_to(self.docs_root.parent)
                except ValueError:
                    rel_path = file_path
                print(f"⚠️  [C-10 祖父] {rel_path}: 历史遗留大写文件（不阻断，请在下次 Wave 迁移至小写）")
                return False
            else:
                # 新建大写文件：硬阻断
                self._report_naming_error(
                    file_path,
                    "新建文件名含大写字母（违反单轨小写标准）",
                    f"请改为全小写 kebab-case，如：{filename.lower().replace('_', '-')}"
                )
                return True

        # 其他不合规格式（既非小写也非大写，但通过了前面所有检查）：警告
        try:
            rel_path = file_path.relative_to(self.docs_root.parent)
        except ValueError:
            rel_path = file_path
        print(f"⚠️  [C-10 警告] {rel_path}: 命名格式异常，建议使用全小写 kebab-case")
        return False

    def _report_naming_error(self, file_path: Path, reason: str, suggestion: str):
        """输出命名违规错误（阻断级）"""
        try:
            rel_path = file_path.relative_to(self.docs_root.parent)
        except ValueError:
            rel_path = file_path
        print(f"❌ [C-10] {rel_path}: {reason}")
        print(f"   建议: {suggestion}")

    # ─── 批量检查 ──────────────────────────────────────────────────

    def check_single_file(self, file_path: Path) -> int:
        """对单个文件执行所有检查，返回退出码"""
        self.reset()
        has_blocking = False
        has_warning = False

        # D-01: 双 YAML
        result = self.check_double_yaml(file_path)
        if result:
            self.blocking_errors.append(result)
            has_blocking = True

        # D-02: BOM（项目标准为 UTF-8 BOM，BOM 本身不是缺陷；
        #   仅在 --scan-bom 模式下报告，pre-commit 不检查）

        # D-03: 无效内链
        link_results = self.check_internal_links(file_path)
        for lr in link_results:
            if lr.get('is_archive'):
                self.warnings.append(lr)
                has_warning = True
            else:
                self.blocking_errors.append(lr)
                has_blocking = True

        # D-05: 编码损坏
        result = self.check_encoding(file_path)
        if result:
            self.blocking_errors.append(result)
            has_blocking = True

        # D-06: 目录映射（升级为阻止级错误，防止映射缺失）
        result = self.check_sitemap_sync(file_path)
        if result:
            self.blocking_errors.append(result)
            has_blocking = True

        self._print_results()

        if has_blocking:
            return 1
        elif has_warning:
            return 2
        return 0

    def check_staged_files(self) -> int:
        """检查 git 暂存区中的 .md 文件"""
        import subprocess

        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
                capture_output=True, text=True, cwd=PROJECT_ROOT
            )
            staged_files = [
                PROJECT_ROOT / f
                for f in result.stdout.strip().split('\n')
                if f.endswith('.md') and f.startswith('docs/')
            ]
        except (subprocess.SubprocessError, OSError):
            print("⚠ 无法获取 git 暂存文件列表，跳过检查")
            return 0

        if not staged_files:
            return 0

        return self.check_file_list(staged_files)

    def check_file_list(self, file_paths: List[Path]) -> int:
        """对文件列表执行所有检查"""
        self.reset()
        has_blocking = False
        has_warning = False

        for fp in file_paths:
            if not fp.exists() or not fp.suffix == '.md':
                continue

            # D-01
            result = self.check_double_yaml(fp)
            if result:
                self.blocking_errors.append(result)
                has_blocking = True

            # D-02: BOM（项目标准为 UTF-8 BOM，跳过）

            # D-03
            link_results = self.check_internal_links(fp)
            for lr in link_results:
                if lr.get('is_archive'):
                    self.warnings.append(lr)
                    has_warning = True
                else:
                    self.blocking_errors.append(lr)
                    has_blocking = True

            # D-05
            result = self.check_encoding(fp)
            if result:
                self.blocking_errors.append(result)
                has_blocking = True

            # D-06
            result = self.check_sitemap_sync(fp)
            if result:
                self.warnings.append(result)
                has_warning = True

        # D-04: module_id 唯一性（需要全量扫描）
        dup_results = self.check_module_id_uniqueness(file_paths)
        for dr in dup_results:
            self.blocking_errors.append(dr)
            has_blocking = True

        self._print_results()

        if has_blocking:
            return 1
        elif has_warning:
            return 2
        return 0

    def check_full(self) -> int:
        """全量扫描（CI/CD 模式）"""
        self.reset()
        all_md_files = list(self.docs_root.rglob('*.md'))
        has_blocking = False
        has_warning = False

        print(f"🔍 全量扫描 {len(all_md_files)} 个 .md 文件...")

        # D-01 + D-05: 逐文件检查（D-02 BOM 为项目标准，不检查）
        for i, fp in enumerate(all_md_files):
            if (i + 1) % 500 == 0:
                print(f"  进度: {i+1}/{len(all_md_files)}")

            # D-01
            result = self.check_double_yaml(fp)
            if result:
                self.blocking_errors.append(result)
                has_blocking = True

            # D-05
            result = self.check_encoding(fp)
            if result:
                self.blocking_errors.append(result)
                has_blocking = True

        # D-04: module_id 唯一性
        print("  检查 module_id 唯一性...")
        dup_results = self.check_module_id_uniqueness(all_md_files)
        for dr in dup_results:
            self.blocking_errors.append(dr)
            has_blocking = True

        # D-03: 内链检查（全量模式委托给 link_checker.py）
        print("  提示: 内链全量检查请运行 python scripts/ci_audit/link_checker.py")

        self._print_results()

        if has_blocking:
            return 1
        elif has_warning:
            return 2
        return 0

    # ─── 单项扫描 ──────────────────────────────────────────────────

    def scan_bom(self) -> int:
        """全量 BOM 扫描"""
        self.reset()
        all_md_files = list(self.docs_root.rglob('*.md'))
        count = 0
        for fp in all_md_files:
            result = self.check_bom(fp)
            if result:
                self.blocking_errors.append(result)
                count += 1
        print(f"\nBOM 扫描结果: {count} 个文件包含 BOM")
        self._print_results()
        return 1 if count > 0 else 0

    def scan_double_yaml(self) -> int:
        """全量双 YAML 扫描"""
        self.reset()
        all_md_files = list(self.docs_root.rglob('*.md'))
        count = 0
        for fp in all_md_files:
            result = self.check_double_yaml(fp)
            if result:
                self.blocking_errors.append(result)
                count += 1
        print(f"\n双 YAML 扫描结果: {count} 个文件包含双 frontmatter")
        self._print_results()
        return 1 if count > 0 else 0

    def scan_encoding(self) -> int:
        """全量编码扫描"""
        self.reset()
        all_md_files = list(self.docs_root.rglob('*.md'))
        count = 0
        for fp in all_md_files:
            result = self.check_encoding(fp)
            if result:
                self.blocking_errors.append(result)
                count += 1
        print(f"\n编码扫描结果: {count} 个文件存在编码问题")
        self._print_results()
        return 1 if count > 0 else 0

    def scan_module_id(self) -> int:
        """全量 module_id 唯一性扫描"""
        self.reset()
        all_md_files = list(self.docs_root.rglob('*.md'))
        dup_results = self.check_module_id_uniqueness(all_md_files)
        for dr in dup_results:
            self.blocking_errors.append(dr)
        print(f"\nmodule_id 扫描结果: {len(dup_results)} 组重复")
        self._print_results()
        return 1 if dup_results else 0

    def scan_links(self) -> int:
        """全量内链扫描（增量版，完整版请用 scripts/ci_audit/link_checker.py）"""
        self.reset()
        all_md_files = list(self.docs_root.rglob('*.md'))
        count = 0
        for i, fp in enumerate(all_md_files):
            if (i + 1) % 500 == 0:
                print(f"  进度: {i+1}/{len(all_md_files)}")
            link_results = self.check_internal_links(fp)
            for lr in link_results:
                if lr.get('is_archive'):
                    self.warnings.append(lr)
                else:
                    self.blocking_errors.append(lr)
                count += 1
        print(f"\n内链扫描结果: {count} 条无效链接")
        self._print_results()
        return 1 if self.blocking_errors else (2 if self.warnings else 0)

    # ─── BOM 清除 ──────────────────────────────────────────────────

    def strip_bom(self, file_path: Path) -> bool:
        """清除文件的 BOM 字符"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            if content.startswith(b'\xef\xbb\xbf'):
                with open(file_path, 'wb') as f:
                    f.write(content[3:])
                return True
        except OSError:
            pass
        return False

    def strip_all_bom(self) -> int:
        """清除所有 .md 文件的 BOM"""
        all_md_files = list(self.docs_root.rglob('*.md'))
        count = 0
        for fp in all_md_files:
            if self.strip_bom(fp):
                count += 1
                print(f"  已清除 BOM: {fp.relative_to(self.docs_root.parent)}")
        print(f"\n共清除 {count} 个文件的 BOM")
        return count

    # ─── 输出 ──────────────────────────────────────────────────────

    def _print_results(self):
        """打印检查结果"""
        if self.blocking_errors:
            print(f"\n❌ 阻止提交的缺陷 ({len(self.blocking_errors)}):")
            for err in self.blocking_errors:
                line_info = f":{err['line']}" if err.get('line') else ""
                print(f"  [{err['type']}] {err['file']}{line_info} — {err['detail']}")

        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)}):")
            for warn in self.warnings:
                line_info = f":{warn['line']}" if warn.get('line') else ""
                print(f"  [{warn['type']}] {warn['file']}{line_info} — {warn['detail']}")

        if not self.blocking_errors and not self.warnings:
            print("✅ 文档质量检查全部通过")


def main():
    parser = argparse.ArgumentParser(
        description='文档缺陷防护 pre-commit 钩子',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--check', choices=['single', 'staged', 'full'],
        help='检查模式: single=单文件, staged=暂存文件, full=全量'
    )
    parser.add_argument(
        '--file', type=str,
        help='单文件检查的文件路径'
    )
    parser.add_argument(
        '--scan-bom', action='store_true',
        help='全量 BOM 扫描'
    )
    parser.add_argument(
        '--scan-double-yaml', action='store_true',
        help='全量双 YAML 扫描'
    )
    parser.add_argument(
        '--scan-encoding', action='store_true',
        help='全量编码扫描'
    )
    parser.add_argument(
        '--scan-module-id', action='store_true',
        help='全量 module_id 唯一性扫描'
    )
    parser.add_argument(
        '--scan-links', action='store_true',
        help='全量内链扫描'
    )
    parser.add_argument(
        '--strip-bom', action='store_true',
        help='清除所有 .md 文件的 BOM'
    )
    parser.add_argument(
        '--check-naming', action='store_true',
        help='检查文件命名规范（单文件模式）'
    )
    parser.add_argument(
        '--docs-root', type=str, default=str(DOCS_ROOT),
        help='docs 根目录路径'
    )

    args, remaining_args = parser.parse_known_args()
    checker = DocGuardChecker(Path(args.docs_root))

    # 单项扫描
    if args.scan_bom:
        sys.exit(checker.scan_bom())
    if args.scan_double_yaml:
        sys.exit(checker.scan_double_yaml())
    if args.scan_encoding:
        sys.exit(checker.scan_encoding())
    if args.scan_module_id:
        sys.exit(checker.scan_module_id())
    if args.scan_links:
        sys.exit(checker.scan_links())
    if args.strip_bom:
        checker.strip_all_bom()
        sys.exit(0)
    if args.check_naming:
        # 双模式支持：
        #   1. pre-commit 模式（pass_filenames:true）：文件路径作为位置参数传入
        #   2. CI 管道模式：文件路径经 stdin 传入（如 find docs/ -name "*.md" | python script.py --check-naming）
        filenames = [f for f in remaining_args if not f.startswith('-')]

        if not filenames and not sys.stdin.isatty():
            # CI 管道模式：从 stdin 读取文件名列表
            filenames = [line.strip() for line in sys.stdin if line.strip()]

        has_error = False
        for file_path_str in filenames:
            if file_path_str:
                result = checker.check_naming_single(Path(file_path_str))
                if result:
                    has_error = True
        sys.exit(1 if has_error else 0)

    # 检查模式
    if args.check == 'single':
        if not args.file:
            print("❌ --check single 需要指定 --file 参数")
            sys.exit(1)
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = PROJECT_ROOT / file_path
        sys.exit(checker.check_single_file(file_path))
    elif args.check == 'staged':
        sys.exit(checker.check_staged_files())
    elif args.check == 'full':
        sys.exit(checker.check_full())

    # 默认：暂存文件检查
    sys.exit(checker.check_staged_files())


if __name__ == '__main__':
    main()
