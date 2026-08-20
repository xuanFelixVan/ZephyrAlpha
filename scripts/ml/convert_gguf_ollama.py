#!/usr/bin/env python
# [BLUEPRINT] MOD-NLP-PIPELINE | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 6
# [MODULE] scripts.ml.convert_gguf_ollama
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] subprocess（llama.cpp convert_hf_to_gguf.py / llama-quantize / ollama CLI，外部进程）
# [CONSUMERS] (CLI 转换脚本，无模块消费者)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 单一推理源原则（§3.1.13 H）：SFT adapter 转 GGUF 回灌 Ollama，禁止新建独立推理服务；adapter 目录不存在→exit 1；--dry-run 只打印命令计划不执行；外部命令非零返回→exit 1
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 6
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] adapter 目录/llama.cpp 脚本缺失→exit 1；子进程失败→exit 1
# [TESTS] tests/scripts/test_ml_convert_gguf_ollama.py
# [TTL] permanent
"""convert_gguf_ollama.py — P1-E3 Phase 6: LoRA adapter 转 GGUF 回灌 Ollama。

单一推理源原则（13 号 §3.1.13 H）：训练轨（SFT/RLSP）用 torch/QLoRA，产物转
GGUF 回灌 Ollama，保持推理路径统一（复用 production local_model 层），
禁止为 SFT 产物新建独立推理服务。

四步管道:
  1. merge   —— peft ``merge_and_unload`` 把 LoRA adapter 合并进基座（HF 格式）
  2. convert —— llama.cpp ``convert_hf_to_gguf.py`` 转 GGUF（默认 f16）
  3. quantize —— ``llama-quantize`` 量化（默认 Q4_K_M，RTX 3090/Ollama 友好）
  4. register —— 生成 Ollama Modelfile + ``ollama create`` 注册模型

用法:
    # 干跑（只打印命令计划，不执行——施工交付态默认）
    python scripts/ml/convert_gguf_ollama.py --dry-run
    # 实际转换（需 llama.cpp 与 ollama CLI 就绪）
    python scripts/ml/convert_gguf_ollama.py --llama-cpp-dir D:/tools/llama.cpp

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 6
SSoT: #ARCH-NLP-PIPELINE-001
"""

from __future__ import annotations

import argparse
import logging
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DEFAULT_ADAPTER_DIR = ROOT / "models" / "qwen25-7b-sft-v1"
DEFAULT_BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
DEFAULT_OUTPUT_NAME = "qwen25-7b-sft-v1"
DEFAULT_QUANT_TYPE = "Q4_K_M"
DEFAULT_OUTTYPE = "f16"

# merge 内联脚本（peft 合并 LoRA → HF 全量模型目录）
_MERGE_SNIPPET = (
    "import sys;"
    "from peft import AutoPeftModelForCausalLM;"
    "from transformers import AutoTokenizer;"
    "m=AutoPeftModelForCausalLM.from_pretrained(sys.argv[1]).merge_and_unload();"
    "m.save_pretrained(sys.argv[2]);"
    "t=AutoTokenizer.from_pretrained(sys.argv[1]);"
    "t.save_pretrained(sys.argv[2])"
)


@dataclass(frozen=True)
class ConvertPlan:
    """四步命令计划（dry-run 打印与实际执行共用同一真源）。"""

    merge_cmd: list[str]
    convert_cmd: list[str]
    quantize_cmd: list[str]
    ollama_cmd: list[str]
    modelfile_text: str
    merged_dir: Path
    gguf_f16: Path
    gguf_quant: Path
    modelfile_path: Path

    def steps(self) -> list[tuple[str, list[str]]]:
        return [
            ("merge", self.merge_cmd),
            ("convert", self.convert_cmd),
            ("quantize", self.quantize_cmd),
            ("ollama_create", self.ollama_cmd),
        ]


def build_merge_command(adapter_dir: Path, merged_dir: Path) -> list[str]:
    """步骤 1：peft merge_and_unload 合并 adapter 进基座（内联 python）。"""
    return [sys.executable, "-c", _MERGE_SNIPPET, str(adapter_dir), str(merged_dir)]


def build_convert_command(llama_cpp_dir: Path, merged_dir: Path, out_gguf: Path, outtype: str) -> list[str]:
    """步骤 2：llama.cpp convert_hf_to_gguf.py 转 GGUF。"""
    script = llama_cpp_dir / "convert_hf_to_gguf.py"
    return [sys.executable, str(script), str(merged_dir), "--outfile", str(out_gguf), "--outtype", outtype]


def build_quantize_command(llama_cpp_dir: Path, in_gguf: Path, out_gguf: Path, qtype: str) -> list[str]:
    """步骤 3：llama-quantize 量化（Windows 加 .exe 后缀由 _quantize_bin 处理）。"""
    return [_quantize_bin(llama_cpp_dir), str(in_gguf), str(out_gguf), qtype]


def _quantize_bin(llama_cpp_dir: Path) -> str:
    """llama-quantize 可执行文件路径（Windows 优先 .exe）。"""
    exe = llama_cpp_dir / "llama-quantize.exe"
    if exe.exists():
        return str(exe)
    return str(llama_cpp_dir / "llama-quantize")


def render_modelfile(gguf_path: Path, model_name: str) -> str:
    """步骤 4a：Ollama Modelfile（FROM 量化后 GGUF；问答模板沿用 Qwen2.5-Instruct）。"""
    return (
        f"FROM {gguf_path.as_posix()}\n"
        f"# {model_name} — SFT adapter GGUF 回灌（13 号 Phase 6 单一推理源）\n"
        "PARAMETER temperature 0.0\n"
    )


def build_ollama_create_command(model_name: str, modelfile_path: Path) -> list[str]:
    """步骤 4b：ollama create 注册模型。"""
    return ["ollama", "create", model_name, "-f", str(modelfile_path)]


def build_plan(
    adapter_dir: Path,
    llama_cpp_dir: Path,
    output_dir: Path,
    model_name: str,
    qtype: str = DEFAULT_QUANT_TYPE,
    outtype: str = DEFAULT_OUTTYPE,
) -> ConvertPlan:
    """组装四步命令计划（纯函数，dry-run 与执行共用）。"""
    merged_dir = output_dir / f"{model_name}-merged-hf"
    gguf_f16 = output_dir / f"{model_name}-{outtype}.gguf"
    gguf_quant = output_dir / f"{model_name}-{qtype}.gguf"
    modelfile_path = output_dir / f"{model_name}.Modelfile"
    return ConvertPlan(
        merge_cmd=build_merge_command(adapter_dir, merged_dir),
        convert_cmd=build_convert_command(llama_cpp_dir, merged_dir, gguf_f16, outtype),
        quantize_cmd=build_quantize_command(llama_cpp_dir, gguf_f16, gguf_quant, qtype),
        ollama_cmd=build_ollama_create_command(model_name, modelfile_path),
        modelfile_text=render_modelfile(gguf_quant, model_name),
        merged_dir=merged_dir,
        gguf_f16=gguf_f16,
        gguf_quant=gguf_quant,
        modelfile_path=modelfile_path,
    )


def print_plan(plan: ConvertPlan) -> None:
    """dry-run 打印命令计划。"""
    print("=" * 60)
    print("GGUF 回灌 Ollama 命令计划（dry-run，未执行）")
    print("=" * 60)
    for name, cmd in plan.steps():
        print(f"\n[{name}]")
        print("  " + shlex.join(str(c) for c in cmd))
    print("\n[modelfile]")
    print(plan.modelfile_text)


def run_plan(plan: ConvertPlan, *, dry_run: bool) -> int:
    """执行命令计划；dry-run 只打印。任一步非零返回 → 1。"""
    if dry_run:
        print_plan(plan)
        return 0
    plan.modelfile_path.write_text(plan.modelfile_text, encoding="utf-8")
    log.info("Modelfile 已写入 %s", plan.modelfile_path)
    for name, cmd in plan.steps():
        log.info("执行 %s: %s", name, shlex.join(str(c) for c in cmd))
        proc = subprocess.run([str(c) for c in cmd], check=False)  # noqa: S603
        if proc.returncode != 0:
            log.error("%s 失败（exit %d）", name, proc.returncode)
            return 1
    log.info("GGUF 回灌完成：ollama run %s 可用", plan.ollama_cmd[2])
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LoRA adapter 转 GGUF 回灌 Ollama（Phase 6）")
    parser.add_argument("--adapter-dir", type=Path, default=DEFAULT_ADAPTER_DIR, help="LoRA adapter 目录")
    parser.add_argument("--llama-cpp-dir", type=Path, default=None, help="llama.cpp 目录（实际执行必填）")
    parser.add_argument("--output-dir", type=Path, default=None, help="产物目录（默认 <adapter-dir 父目录>/gguf）")
    parser.add_argument("--model-name", default=DEFAULT_OUTPUT_NAME, help="Ollama 注册模型名")
    parser.add_argument("--quantize", default=DEFAULT_QUANT_TYPE, help="量化类型（默认 Q4_K_M）")
    parser.add_argument("--outtype", default=DEFAULT_OUTTYPE, help="GGUF 中间精度（默认 f16）")
    parser.add_argument("--dry-run", action="store_true", help="只打印命令计划不执行")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if not args.adapter_dir.is_dir():
        log.error("adapter 目录不存在: %s（先完成 Phase 4 SFT 训练）", args.adapter_dir)
        sys.exit(1)

    output_dir = args.output_dir or (args.adapter_dir.parent / "gguf")
    plan = build_plan(
        adapter_dir=args.adapter_dir,
        llama_cpp_dir=args.llama_cpp_dir or Path("llama.cpp"),
        output_dir=output_dir,
        model_name=args.model_name,
        qtype=args.quantize,
        outtype=args.outtype,
    )

    if not args.dry_run:
        if args.llama_cpp_dir is None:
            log.error("实际执行须指定 --llama-cpp-dir（convert_hf_to_gguf.py 所在目录）")
            sys.exit(1)
        if not (args.llama_cpp_dir / "convert_hf_to_gguf.py").exists():
            log.error("llama.cpp 转换脚本缺失: %s", args.llama_cpp_dir / "convert_hf_to_gguf.py")
            sys.exit(1)
        output_dir.mkdir(parents=True, exist_ok=True)

    sys.exit(run_plan(plan, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
