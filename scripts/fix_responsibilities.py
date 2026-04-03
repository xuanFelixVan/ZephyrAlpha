#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职责边界修正脚本
用于修正DataCleaner和DataNormalizer的职责边界，移除"质量评估"职责
"""

import os
import sys

def fix_datacleaner_responsibilities():
    """修正DataCleaner的职责边界"""
    file_path = r"d:\ZephyrAlpha\docs\05_IMPLEMENTATION\05_TECHNICAL_SPECIFICATIONS\DATACLEANER_TECHNICAL_SPECIFICATION.md"
    
    try:
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"成功使用 {encoding} 编码读取文件")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if content is None:
            print("无法读取文件，尝试所有编码都失败")
            return False
        
        # 查找并替换职责边界部分
        old_text = """### 2.3 模块职责与边界定义
- **核心职责**: 数据清洗、缺失值处理、异常值检测、价格复权、数据对齐、格式标准化、质量评估
- **职责边界**: 
  - ✅ 本模块负责: 数据清洗、缺失值处理、异常值检测、价格复权、数据对齐、格式标准化
  - ❌ 本模块不负责: 数据获取、因子计算、数据持久化、数据分析
- **接口契约**: 提供统一的Python API接口"""
        
        new_text = """### 2.3 模块职责与边界定义
- **核心职责**: 数据清洗、缺失值处理、异常值检测、价格复权、数据对齐、格式标准化、**清洗效果评估**
- **职责边界**: 
  - ✅ **本模块负责**: 数据清洗、缺失值处理、异常值检测、价格复权、数据对齐、格式标准化、清洗效果评估
  - ❌ **本模块不负责**: 数据获取、因子计算、数据持久化、数据分析、**数据质量校验**（由DataValidator负责）、**数据质量监控**（由RealtimeQualityMonitor负责）、**数据质量评分**（由QualityScoringSystem负责）
- **接口契约**: 提供统一的Python API接口

**⚠️ 职责澄清**:
- 本模块的"清洗效果评估"仅指评估清洗操作本身的效果（如缺失值填充率、异常值处理率），**不负责**数据质量的全面评估
- 数据质量的全面评估由**DataValidator**（静态校验）、**RealtimeQualityMonitor**（实时监控）、**QualityScoringSystem**（质量评分）三个模块共同负责"""
        
        if old_text in content:
            content = content.replace(old_text, new_text)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 成功修正DataCleaner职责边界")
            return True
        else:
            print("⚠️ 未找到需要替换的内容，可能已经修改过")
            return False
            
    except Exception as e:
        print(f"❌ 修正DataCleaner职责边界失败: {e}")
        return False

def fix_datanormalizer_responsibilities():
    """修正DataNormalizer的职责边界"""
    file_path = r"d:\ZephyrAlpha\docs\05_IMPLEMENTATION\05_TECHNICAL_SPECIFICATIONS\DATANORMALIZER_TECHNICAL_SPECIFICATION.md"
    
    try:
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"成功使用 {encoding} 编码读取文件")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if content is None:
            print("无法读取文件，尝试所有编码都失败")
            return False
        
        # 查找并替换职责边界部分
        old_text = """### 2.3 模块职责与边界定义
- **核心职责**: 数据标准化、归一化、数据转换、质量评估
- **职责边界**: 
  - ✅ 本模块负责: 数据标准化、归一化、数据转换、质量评估
  - ❌ 本模块不负责: 数据清洗、因子计算、模型训练
- **接口契约**: 提供统一的Python API接口"""
        
        new_text = """### 2.3 模块职责与边界定义
- **核心职责**: 数据标准化、归一化、数据转换、**标准化效果评估**
- **职责边界**: 
  - ✅ **本模块负责**: 数据标准化、归一化、数据转换、标准化效果评估
  - ❌ **本模块不负责**: 数据清洗、因子计算、模型训练、**数据质量校验**（由DataValidator负责）、**数据质量监控**（由RealtimeQualityMonitor负责）、**数据质量评分**（由QualityScoringSystem负责）
- **接口契约**: 提供统一的Python API接口

**⚠️ 职责澄清**:
- 本模块的"标准化效果评估"仅指评估标准化操作本身的效果（如数据分布变化、极端值处理效果），**不负责**数据质量的全面评估
- 数据质量的全面评估由**DataValidator**（静态校验）、**RealtimeQualityMonitor**（实时监控）、**QualityScoringSystem**（质量评分）三个模块共同负责"""
        
        if old_text in content:
            content = content.replace(old_text, new_text)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 成功修正DataNormalizer职责边界")
            return True
        else:
            print("⚠️ 未找到需要替换的内容，可能已经修改过")
            return False
            
    except Exception as e:
        print(f"❌ 修正DataNormalizer职责边界失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("开始修正职责边界问题")
    print("=" * 60)
    
    # 修正DataCleaner
    print("\n1. 修正DataCleaner职责边界...")
    result1 = fix_datacleaner_responsibilities()
    
    # 修正DataNormalizer
    print("\n2. 修正DataNormalizer职责边界...")
    result2 = fix_datanormalizer_responsibilities()
    
    print("\n" + "=" * 60)
    if result1 and result2:
        print("✅ 所有职责边界修正完成")
    else:
        print("⚠️ 部分职责边界修正失败，请检查")
    print("=" * 60)

if __name__ == "__main__":
    main()
