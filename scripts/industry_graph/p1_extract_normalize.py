# [MODULE] scripts.industry_graph.p1_extract_normalize
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); scripts.industry_graph.p0_scan_documents
# [CONSUMERS] P2 文字提取流水线
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只处理 is_canonical=true 且未排除的压缩包; zip内同名JPG/PDF只留PDF; 解压产物登记ig_document并参与全库去重分组; 不改动源目录
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单包解压失败->记warn继续; unrar不可用->跳过rar并提示
# [TTL] permanent
"""P1 解压归一 + 内容级二次去重。

对 ig_document 中 canonical 的压缩包（.zip 必处理，.rar 需系统有 UnRAR）：
1. 解压到 STAGING 目录（按 dedup_group 分包，避免同名覆盖）；
2. 归一规则：同包内 同名.jpg/.jpeg/.png 与 .pdf 并存时只留 PDF（图片为同一内容的导出件）；
3. 产物文件计算 MD5 登记 ig_document（doc_type 按扩展名推导，parent_doc 指向来源包）；
4. 全库重算 dedup 分组与 is_canonical（同 hash 同组，zip 内 PDF 与散放 PDF 重复即被折叠）。

用法::

    python scripts/industry_graph/p1_extract_normalize.py
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from psycopg2.extras import execute_values

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

STAGING = Path(r"E:\数据下载\产业链数据_P1归一")
_UNRAR_CANDIDATES = (
    r"E:\7-Zip\Files\7-Zip\7z.exe",  # 2026-08-27 管理安装(免提权)部署
    r"C:\Program Files\7-Zip\7z.exe",
    r"C:\Program Files (x86)\7-Zip\7z.exe",
    r"C:\Program Files\WinRAR\UnRAR.exe",
    r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
)
_IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
# zip 内图片若是 PDF 的导出件（幻灯片页/封面首图/同名图），归一时删除
_SLIDE_RE = re.compile(r"^(幻灯片|slide|p)\s*\d+$", re.IGNORECASE)


def _is_derived_image(img: Path, pdf_stems: set[str]) -> bool:
    stem = img.stem
    return stem in pdf_stems or bool(_SLIDE_RE.match(stem)) or "首图" in stem


def _md5(path: Path, chunk: int = 4 << 20) -> str | None:
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while True:
                buf = f.read(chunk)
                if not buf:
                    break
                h.update(buf)
        return h.hexdigest()
    except OSError as exc:
        print(f"[WARN] 读取失败 hash 置空: {path} ({exc})")
        return None


def _find_unrar() -> str | None:
    for c in _UNRAR_CANDIDATES:
        if os.path.isfile(c):
            return c
    return shutil.which("unrar") or shutil.which("7z")


def _find_bsdtar() -> str | None:
    """Windows 10+ 自带 bsdtar（tar.exe），可读多数 RAR。"""
    tar = r"C:\Windows\System32\tar.exe"
    return tar if os.path.isfile(tar) else shutil.which("tar")


def _zip_member_name(info: zipfile.ZipInfo) -> str:
    """国内打包工具常用 GBK 命名但 zipfile 按 cp437 解码，需转码恢复中文名。"""
    try:
        return info.filename.encode("cp437").decode("gbk")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return info.filename


def _extract_zip(src: Path, out_dir: Path) -> None:
    base = out_dir.resolve()
    with zipfile.ZipFile(src) as zf:
        for info in zf.infolist():
            target = (base / _zip_member_name(info)).resolve()
            if not str(target).startswith(str(base)):  # zip slip 防护
                continue
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as sf, open(target, "wb") as df:
                shutil.copyfileobj(sf, df)


def _normalize_dir(d: Path) -> tuple[int, int]:
    """包内含 PDF 时，删除其派生图片（幻灯片页/首图/同名图）；无 PDF 的图片包原样保留。
    返回 (删除数, 保留文件数)。"""
    pdf_stems = {p.stem for p in d.rglob("*.pdf")}
    if not pdf_stems:
        return 0, sum(1 for _ in d.rglob("*") if _.is_file())
    removed = 0
    for ext in _IMG_EXT:
        for img in d.rglob(f"*{ext}"):
            if _is_derived_image(img, pdf_stems):
                img.unlink()
                removed += 1
    return removed, sum(1 for _ in d.rglob("*") if _.is_file())


def main() -> int:
    conn = get_depgraph_pg_connection(read_only=False, autocommit=False)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT doc_id, relative_path, source_root, dedup_group
            FROM ig_document
            WHERE doc_type='archive' AND is_canonical AND NOT excluded
            ORDER BY relative_path
            """
        )
        packs = cur.fetchall()
    print(f"[P1] canonical 压缩包 {len(packs)} 个")

    unrar = _find_unrar()
    bsdtar = _find_bsdtar()
    print(f"[P1] unrar/7z: {unrar or '不可用'}; bsdtar: {bsdtar or '不可用'}")
    # 全量重建（幂等）：清空暂存目录 + 删除上一轮 P1 登记行，防止乱码/残留产物二次登记
    staging_resolved = STAGING.resolve()
    assert str(staging_resolved) == r"E:\数据下载\产业链数据_P1归一", "STAGING 路径守卫"
    if staging_resolved.exists():
        shutil.rmtree(staging_resolved)
    STAGING.mkdir(parents=True, exist_ok=True)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM ig_document WHERE parent_doc IS NOT NULL")
    conn.commit()

    prod_rows, done, failed = [], 0, 0
    for doc_id, rel, src_root, dg in packs:
        src = Path(src_root) / rel
        out_dir = STAGING / (dg or doc_id)
        try:
            if src.suffix.lower() == ".zip":
                _extract_zip(src, out_dir)
            elif src.suffix.lower() == ".rar":
                # 优先 7z/UnRAR（支持 RAR5），bsdtar 兜底（不支持 RAR5）
                if unrar:
                    if unrar.lower().endswith("7z.exe"):
                        subprocess.run([unrar, "x", str(src), f"-o{out_dir}", "-y"], check=True, capture_output=True)
                    else:
                        subprocess.run(
                            [unrar, "x", "-y", str(src), str(out_dir) + os.sep], check=True, capture_output=True
                        )
                elif bsdtar:
                    subprocess.run([bsdtar, "-xf", str(src), "-C", str(out_dir)], check=True, capture_output=True)
                else:
                    print(f"[WARN] 跳过 rar（无解压器）: {rel}")
                    continue
            else:
                continue
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"[WARN] 解压失败: {rel} ({exc})")
            continue

        parent_bundle = re.split(r"[\\/]", rel)[0]
        removed, _kept = _normalize_dir(out_dir)
        for p in out_dir.rglob("*"):
            if not p.is_file():
                continue
            frel = str(p.relative_to(STAGING))
            fh = _md5(p)
            ext = p.suffix.lower()
            if ext == ".pdf":
                dtype = "panorama_pdf"
            elif ext in _IMG_EXT:
                dtype = "atlas_image"
            else:
                dtype = "other"
            prod_rows.append(
                (
                    "DOC-" + hashlib.md5(("P1\\" + frel).encode("utf-8")).hexdigest()[:20],
                    frel,
                    str(STAGING),
                    doc_id,
                    parent_bundle,
                    p.name,
                    ext,
                    p.stat().st_size,
                    datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc),
                    fh,
                    "DG-" + fh[:16] if fh else None,
                    True,
                    dtype,
                    p.stem,
                    None,
                    None,
                    False,
                    None,
                )
            )
        done += 1
        if done % 50 == 0:
            print(f"[PROGRESS] 已处理 {done}/{len(packs)} 包（产物 {len(prod_rows)}，归一删图累计）")

    print(f"[P1] 解压完成 {done} 包，失败 {failed}，产物文件 {len(prod_rows)} 个，开始登记 ...")

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO ig_document (
                doc_id, relative_path, source_root, parent_doc, bundle, file_name, ext,
                size_bytes, mtime, file_hash, dedup_group, is_canonical, doc_type,
                title, year, org, excluded, exclude_reason
            ) VALUES %s
            ON CONFLICT (doc_id) DO UPDATE SET
                file_hash = EXCLUDED.file_hash, dedup_group = EXCLUDED.dedup_group,
                doc_type = EXCLUDED.doc_type, bundle = EXCLUDED.bundle, updated_at = now()
            """,
            prod_rows,
            page_size=1000,
        )
        # 全库重算 canonical（同组字典序最小者）
        cur.execute(
            """
            UPDATE ig_document d
            SET is_canonical = (d.relative_path = sub.min_path), updated_at = now()
            FROM (
                SELECT dedup_group, MIN(relative_path) AS min_path
                FROM ig_document WHERE dedup_group IS NOT NULL
                GROUP BY dedup_group
            ) sub
            WHERE d.dedup_group = sub.dedup_group
            """
        )
        # 统计
        cur.execute("SELECT count(*) FROM ig_document WHERE parent_doc IS NOT NULL")
        extracted = cur.fetchone()[0]
        cur.execute(
            """
            SELECT count(*) FROM ig_document
            WHERE doc_type IN ('panorama_pdf','research_report') AND NOT excluded AND is_canonical
            """
        )
        eff_pdf = cur.fetchone()[0]
        cur.execute(
            """
            SELECT count(*) FROM ig_document d
            WHERE d.parent_doc IS NOT NULL AND NOT d.is_canonical
              AND EXISTS (SELECT 1 FROM ig_document o
                          WHERE o.dedup_group = d.dedup_group AND o.parent_doc IS NULL)
            """
        )
        folded = cur.fetchone()[0]
    conn.commit()
    conn.close()

    print(
        f"[P1] 完成：登记产物 {extracted} 个；其中与既有文件内容重复被折叠 {folded} 个；"
        f"当前有效 PDF 文档（canonical）共 {eff_pdf} 份"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
