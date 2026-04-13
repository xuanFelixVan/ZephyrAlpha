---
module_id: 05_IMPLEMENTATION_07_OPERATIONS_MINICONDA_INSTALLATION_CHECKLIST
layer: layer_05
version: 1.0.0
status: Active
responsibility:
  - Miniconda Installation Checklist相关业务
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
---

## ﻭ۶ ﮒ؟ﻟ۲ﮒﻠ۹ﻟﺁ?

### ﻠ۹ﻟﺁ1: ﮒﺏﻠﮔﮔﻝﭨﻝ،ﺁﻝ۹ﮒ?```

1. ﮒﺏﻠﮒﺛﮒﮔﮔPowerShell/CMDﻝ۹ﮒ۲

2. ﮒﺏﻠVS Codeﺅﺙﮒ۵ﮔﮔﮒﺙﻛﭦﺅﺙ

3. ﮒﺏﻠTrae AIﻝﻝﭨﻝ،ﺁﺅﺙﮒ۵ﮔﻠﻟ۵ﺅﺙ

```



### ﻠ۹ﻟﺁ2: ﻠﮔﺍﮔﮒﺙﻝﭨﻝ،ﺁ

```

1. ﮔ?Win + R

2. ﻟﺝﮒ۴: powershell

3. ﮔﮒﻟﺛ۵ﮔﮒﺙﮔﺍﻝPowerShell

```



### ﻠ۹ﻟﺁ3: ﻟﺟﻟ۰ﻠ۹ﻟﺁﮒﺛﻛﭨ۳

```powershell

# ﮒﺛﻛﭨ۳1: ﮔ۲ﮔ۴condaﻝﮔ؛

conda --version

# ﮒﭦﻟﺁ۴ﮔﺝﻝ۳ﭦ: conda 24.x.x



# ﮒﺛﻛﭨ۳2: ﮔ۲ﮔ۴Pythonﻝﮔ؛

python --version

# ﮒﭦﻟﺁ۴ﮔﺝﻝ۳ﭦ: Python 3.13.xﺅﺙMinicondaﻟ۹ﮒﺕ۵ﻝPythonﺅﺙ?

# ﮒﺛﻛﭨ۳3: ﮔ۲ﮔ۴condaﻝﺁﮒ۱

conda env list

# ﮒﭦﻟﺁ۴ﮔﺝﻝ۳ﭦ: base ﻝﺁﮒ۱

```



```---



## ﻭ ﻝﺁﮒ۱ﻠﻝﺛ؟ﮔﻛﭨﭘﮒﮒﭨﭦ



**ﻛﺕﻟ۵**ﻝﺑﮔ۴ﮒ۷ﻝﭨﻝ،ﺁﻟﺝﮒ۴YAMLﮒﮒ؟ﺗﺅﺙﻟﮔﺁﮒﮒﭨﭦﮔﻛﭨﭘﺅﺙ?

### ﮒﮒﭨﭦ environment.yml ﮔﻛﭨﭘ



```powershell

# ﮒﮒﭨﭦﻝﺁﮒ۱ﻠﻝﺛ؟ﮔﻛﭨﭘ

@'

name: qmt

channels:

  - defaults

dependencies:

  - python=3.12

  - pip

  - pandas

  - numpy

  - pip:

    - xtquant

'@ | Out-File -FilePath environment.yml -Encoding UTF8



# ﻛﺛﺟﻝ۷ﻠﻝﺛ؟ﮔﻛﭨﭘﮒﮒﭨﭦﻝﺁﮒ۱

conda env create -f environment.yml

```



```---



## ﻗﺅﺕ ﮒﺕﺕﻟ۶ﻠﻟﺁﺁﮒﻟ۶۲ﮒﺏﮔﺗﮔ۰?

### ﻠﻟﺁﺁ1: "conda command not found"

**ﮒﮒ**: PATHﻝﺁﮒ۱ﮒﻠﮔﺎ۰ﮔﻠﻝﺛ؟

**ﻟ۶۲ﮒﺏ**:

1. ﻠﮔﺍﮒ؟ﻟ۲Miniconda

2. ﻝ۰؟ﻛﺟﮒﺝﻠ?Add to PATH"

3. ﻠﮒﺁﮔﮔﻝﭨﻝ،?

### ﻠﻟﺁﺁ2: ﮒ؟ﻟ۲ﻝ۷ﮒﭦﻠ۹ﻠ

**ﮒﮒ**: ﮔﻠﻠ؟ﻠ۱

**ﻟ۶۲ﮒﺏ**:

1. ﮒﺏﻠ؟ﻝﺗﮒﭨﮒ؟ﻟ۲ﻝ۷ﮒﭦ

2. ﻠﮔ۸"ﻛﭨ۴ﻝ؟۰ﻝﮒﻟﭦ،ﻛﭨﺛﻟﺟﻟ۰"



### ﻠﻟﺁﺁ3: ﻛﺕﻟﺛﺛﻠﮒﭦ۵ﮔ?**ﻟ۶۲ﮒﺏ**: ﻛﺛﺟﻝ۷ﮒﺛﮒﻠﮒ

```

# ﻠﻝﺛ؟ﮔﺕﮒﻠﮒ

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/

conda config --set show_channel_urls yes

```



```---



## ﻭﺁ ﮒ؟ﻟ۲ﮒ؟ﮔﮒﻝﮔ۲ﻝ۰؟ﮔﻛﺛ



### 1. ﮒﮒﭨﭦQMTﻝﺁﮒ۱

```powershell

# ﮔﺗﮔﺏ1: ﻛﺛﺟﻝ۷ﮒﺛﻛﭨ۳ﻟ۰?conda create -n qmt python=3.12 -y



# ﮔﺗﮔﺏ2: ﻛﺛﺟﻝ۷ﻠﻝﺛ؟ﮔﻛﭨﭘﺅﺙﮔ۷ﻟﺅﺙ

# ﮒﮒﮒﭨ?environment.yml ﮔﻛﭨﭘ

# ﻝﭘﮒﻟﺟﻟ۰: conda env create -f environment.yml

```



### 2. ﮔﺟﮔﺑﭨﻝﺁﮒ۱?```powershell

conda activate qmt

```



### 3. ﻠ۹ﻟﺁPythonﻝﮔ؛

```powershell

python --version

# ﮒﭦﻟﺁ۴ﮔﺝﻝ۳ﭦ: Python 3.12.x

```



### 4. ﮒ؟ﻟ۲xtquant

```powershell

pip install xtquant pandas numpy

```



```
```---
```



## ﻭ ﻠﻟ۵ﮒﺕ؟ﮒ۸ﺅﺙ



**ﮒ۵ﮔﮔ۷ﮒ۷ﮒ؟ﻟ۲ﻟﺟﻝ۷ﻛﺕﻠﮒﺍﻠ؟ﻠ۱ﺅﺙﻟﺁﺓﮔﻛﺝ?*ﺅﺙ?

1. **ﮒ؟ﻟ۲ﻝ۷ﮒﭦﻝﮔ۹ﮒ?*ﺅﺙﻝﺗﮒ،ﮔﺁﻠ،ﻝﭦ۶ﻠﻠ۰ﺗﻠ۰ﭖﻠ۱ﺅﺙ?2. **ﮒ؟ﻟ۲ﻟﺟﻝ۷ﻛﺕﻝﻛﭨﭨﻛﺛﻠﻟﺁﺁﻛﺟ۰ﮔﺁ**

3. **ﮒ؟ﻟ۲ﮒ؟ﮔﮒﻟﺟﻟ۰?`conda --version` ﻝﻟﺝﮒ?*



**ﻠﻟ۵ﮔﻠ**ﺅﺙﻛﺕﻟ۵ﻟﺓﺏﻟﺟ?Add to PATH"ﻠﻠ۰ﺗﺅﺙﻟﺟﮔﺁcondaﮒﺛﻛﭨ۳ﮒﺁﻝ۷ﻝﮒﺏﻠ؟ﻙ?

