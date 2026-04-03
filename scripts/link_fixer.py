"""
文档链接修复工具
自动修复损坏的内部链接

功能:
    - 扫描损坏的链接
    - 尝试自动查找正确的文件位置
    - 生成修复建议
    - 批量修复链接

使用方式:
    python scripts/link_fixer.py --scan
    python scripts/link_fixer.py --fix
    python scripts/link_fixer.py --report
"""
import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class BrokenLink:
    """损坏的链接"""
    file_path: str
    link_text: str
    link_target: str
    line_number: int
    suggested_fix: Optional[str] = None
    fix_type: Optional[str] = None  # 'auto', 'manual', 'skip'


class LinkFixer:
    """
    链接修复器
    
    修复策略:
        1. 自动查找: 在项目中搜索目标文件
        2. 路径修正: 修正相对路径错误
        3. 移除链接: 对于不存在的文件，移除链接
    """
    
    # Markdown链接正则: [text](path)
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    def __init__(self, project_root: str):
        """
        初始化链接修复器
        
        参数:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.broken_links: List[BrokenLink] = []
        self.file_index: Dict[str, Path] = {}  # filename -> file_path
        
        # 构建文件索引
        self._build_file_index()
    
    def _build_file_index(self) -> None:
        """构建文件索引，用于快速查找文件"""
        logger.info("构建文件索引...")
        
        for root, dirs, files in os.walk(self.project_root):
            # 过滤排除目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'A股数据', 'node_modules'}]
            
            for filename in files:
                if filename.endswith('.md'):
                    file_path = Path(root) / filename
                    # 索引文件名（不含路径）
                    if filename not in self.file_index:
                        self.file_index[filename] = file_path
        
        logger.info(f"文件索引构建完成，共索引 {len(self.file_index)} 个文件")
    
    def scan_broken_links(self, file_path: Path) -> List[BrokenLink]:
        """
        扫描文件中的损坏链接
        
        参数:
            file_path: 文件路径
        
        返回:
            List[BrokenLink]: 损坏链接列表
        """
        broken_links = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                matches = self.LINK_PATTERN.findall(line)
                for text, link in matches:
                    # 跳过外部链接和锚点链接
                    if link.startswith(('http://', 'https://', '#', 'mailto:')):
                        continue
                    
                    # 检查链接是否损坏
                    if not self._check_link_valid(file_path, link):
                        broken_link = BrokenLink(
                            file_path=str(file_path.relative_to(self.project_root)),
                            link_text=text,
                            link_target=link,
                            line_number=line_num,
                        )
                        
                        # 尝试自动修复
                        suggested_fix = self._suggest_fix(file_path, link)
                        if suggested_fix:
                            broken_link.suggested_fix = suggested_fix
                            broken_link.fix_type = 'auto'
                        else:
                            broken_link.fix_type = 'manual'
                        
                        broken_links.append(broken_link)
        
        except Exception as e:
            logger.error(f"扫描链接失败: {file_path}, {e}")
        
        return broken_links
    
    def _check_link_valid(self, file_path: Path, link: str) -> bool:
        """检查链接是否有效"""
        # 处理相对路径
        if not link.startswith('/'):
            target_path = (file_path.parent / link).resolve()
        else:
            target_path = (self.project_root / link.lstrip('/')).resolve()
        
        # 检查文件或目录是否存在
        return target_path.exists()
    
    def _suggest_fix(self, file_path: Path, link: str) -> Optional[str]:
        """
        建议修复方案
        
        参数:
            file_path: 包含链接的文件路径
            link: 损坏的链接
        
        返回:
            Optional[str]: 建议的修复路径 (如果可以自动修复)
        """
        # 提取文件名
        link_path = Path(link)
        filename = link_path.name
        
        # 如果链接指向目录，检查目录是否存在
        if link.endswith('/'):
            dir_name = link.rstrip('/')
            # 在文件索引中查找匹配的目录
            for root, dirs, files in os.walk(self.project_root):
                if dir_name in dirs:
                    # 计算相对路径
                    target_dir = Path(root) / dir_name
                    relative_path = os.path.relpath(target_dir, file_path.parent)
                    return relative_path.replace('\\', '/') + '/'
        else:
            # 在文件索引中查找文件
            if filename in self.file_index:
                target_file = self.file_index[filename]
                # 计算相对路径
                relative_path = os.path.relpath(target_file, file_path.parent)
                return relative_path.replace('\\', '/')
        
        return None
    
    def scan_all_files(self) -> List[BrokenLink]:
        """
        扫描所有Markdown文件
        
        返回:
            List[BrokenLink]: 所有损坏链接列表
        """
        logger.info("开始扫描所有文件...")
        
        self.broken_links = []
        
        for root, dirs, files in os.walk(self.project_root):
            # 过滤排除目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'A股数据', 'node_modules'}]
            
            for filename in files:
                if filename.endswith('.md'):
                    file_path = Path(root) / filename
                    broken = self.scan_broken_links(file_path)
                    self.broken_links.extend(broken)
        
        logger.info(f"扫描完成，共发现 {len(self.broken_links)} 个损坏链接")
        return self.broken_links
    
    def generate_fix_report(self) -> Dict:
        """
        生成修复报告
        
        返回:
            Dict: 修复报告
        """
        # 统计修复类型
        fix_types = defaultdict(int)
        for link in self.broken_links:
            fix_types[link.fix_type] += 1
        
        # 按文件分组
        links_by_file = defaultdict(list)
        for link in self.broken_links:
            links_by_file[link.file_path].append(asdict(link))
        
        report = {
            'summary': {
                'scan_time': datetime.now().isoformat(),
                'total_broken_links': len(self.broken_links),
                'auto_fixable': fix_types['auto'],
                'manual_fix_required': fix_types['manual'],
                'files_affected': len(links_by_file),
            },
            'fix_statistics': dict(fix_types),
            'broken_links_by_file': dict(links_by_file),
        }
        
        return report
    
    def save_report(self, report: Dict, output_path: str) -> None:
        """
        保存修复报告
        
        参数:
            report: 修复报告
            output_path: 输出文件路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"修复报告已保存到: {output_file}")
    
    def auto_fix_links(self, dry_run: bool = True) -> Dict:
        """
        自动修复链接
        
        参数:
            dry_run: 是否为演练模式 (不实际修改文件)
        
        返回:
            Dict: 修复结果
        """
        logger.info(f"开始自动修复链接 (dry_run={dry_run})...")
        
        fix_results = {
            'total_attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'details': [],
        }
        
        # 按文件分组
        links_by_file = defaultdict(list)
        for link in self.broken_links:
            if link.fix_type == 'auto':
                links_by_file[link.file_path].append(link)
        
        for file_path, links in links_by_file.items():
            try:
                full_path = self.project_root / file_path
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                for link in links:
                    fix_results['total_attempted'] += 1
                    
                    # 替换链接
                    old_link = f"[{link.link_text}]({link.link_target})"
                    new_link = f"[{link.link_text}]({link.suggested_fix})"
                    
                    if old_link in content:
                        content = content.replace(old_link, new_link)
                        fix_results['successful'] += 1
                        
                        fix_results['details'].append({
                            'file': file_path,
                            'line': link.line_number,
                            'old_link': link.link_target,
                            'new_link': link.suggested_fix,
                            'status': 'success',
                        })
                    else:
                        fix_results['failed'] += 1
                        fix_results['details'].append({
                            'file': file_path,
                            'line': link.line_number,
                            'old_link': link.link_target,
                            'new_link': link.suggested_fix,
                            'status': 'failed',
                            'reason': 'Link not found in content',
                        })
                
                # 写入文件（如果不是演练模式）
                if not dry_run and content != original_content:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"已修复文件: {file_path}")
            
            except Exception as e:
                logger.error(f"修复文件失败: {file_path}, {e}")
                fix_results['failed'] += len(links)
        
        logger.info(f"自动修复完成: 成功 {fix_results['successful']}, 失败 {fix_results['failed']}")
        return fix_results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文档链接修复工具')
    parser.add_argument(
        '--project-root',
        default='d:/ZephyrAlpha',
        help='项目根目录路径'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='扫描损坏的链接'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='自动修复链接'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='演练模式，不实际修改文件'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='生成修复报告'
    )
    parser.add_argument(
        '--output',
        default='docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/link_fix_report.json',
        help='输出报告路径'
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建链接修复器
    fixer = LinkFixer(project_root=args.project_root)
    
    # 扫描损坏链接
    if args.scan or args.fix or args.report:
        broken_links = fixer.scan_all_files()
    
    # 生成报告
    if args.report:
        report = fixer.generate_fix_report()
        fixer.save_report(report, args.output)
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("链接修复报告")
        print("=" * 60)
        print(f"损坏链接总数: {report['summary']['total_broken_links']}")
        print(f"可自动修复: {report['summary']['auto_fixable']}")
        print(f"需手动修复: {report['summary']['manual_fix_required']}")
        print(f"受影响文件数: {report['summary']['files_affected']}")
        print("=" * 60)
    
    # 自动修复
    if args.fix:
        fix_results = fixer.auto_fix_links(dry_run=args.dry_run)
        
        print("\n" + "=" * 60)
        print("链接修复结果")
        print("=" * 60)
        print(f"尝试修复: {fix_results['total_attempted']}")
        print(f"修复成功: {fix_results['successful']}")
        print(f"修复失败: {fix_results['failed']}")
        print("=" * 60)


if __name__ == '__main__':
    main()
