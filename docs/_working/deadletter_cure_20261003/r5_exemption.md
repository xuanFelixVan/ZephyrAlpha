---
r5_digit_suffix_exempt: 目录名已是历史事实（st-deadletter-cure-20261003 战役骨架册在途，他会话文件零触碰禁重命名）；数字后缀=战役日期戳非多真源序号
title: R5 数字后缀目录豁免标记
session: st-sJ-doctorb2-20261004
ttl: task_bound
date: 2026-10-04
---

# R5 豁免标记（r5_exemption.md）

本文件是 `R5-DIGIT-SUFFIX` 门禁的目录级豁免标记（硬拦门位件③处方，2026-10-04）。

- 豁免对象：本目录 `docs/_working/deadletter_cure_20261003/` 的目录名数字后缀
- 豁免理由：目录名是历史事实（死信治愈战役骨架册，`_20261003` 为战役日期戳而非
  `_01/_02` 多真源序号）；目录属他会话（st-deadletter-cure-20261003）在途产物，
  按零触碰纪律不重命名，重命名正门留给该战役收尾会话自行裁量
- 生效机制：`r5_digit_suffix_gate.py::_is_r5_exempt` 读取本文件 frontmatter 的
  非空 `r5_digit_suffix_exempt` 理由即视同历史违规跳过；删除本文件或清空理由即恢复拦截
