# Windows 安装 TensorFlow 指南

## ⚠️ 问题说明

在 Windows 上安装 TensorFlow 时可能遇到以下错误：

```
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory
HINT: This error might have occurred since this system does not have Windows Long Path support enabled.
```

这是因为 Windows 默认不支持长路径（超过 260 个字符的文件路径）。

---

## ✅ 解决方案

### 方法 1: 启用 Windows 长路径支持（推荐）

#### Windows 10/11 家庭版和专业版

1. **使用注册表编辑器**
   ```
   Win + R 打开运行
   输入 regedit
   导航到：HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
   将 LongPathsEnabled 的值改为 1
   重启电脑
   ```

2. **使用组策略编辑器**（专业版）
   ```
   Win + R 打开运行
   输入 gpedit.msc
   计算机配置 → 管理模板 → 系统 → 文件系统
   启用"启用 Win32 长路径"
   重启电脑
   ```

3. **使用 PowerShell**（管理员权限）
   ```powershell
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
       -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

#### 重启后安装 TensorFlow

```bash
pip install tensorflow
```

---

### 方法 2: 使用 TensorFlow CPU 版本（较小）

```bash
pip install tensorflow-cpu
```

---

### 方法 3: 使用 Google Colab（无需本地安装）

如果本地安装困难，可以使用 Google Colab：
- 免费的 GPU/TPU 支持
- 预装 TensorFlow
- 网址：https://colab.research.google.com/

---

## 📦 项目依赖安装

### 基础安装（推荐）

```bash
# 安装核心依赖
pip install pandas numpy tushare scikit-learn matplotlib seaborn plotly

# 可选：安装 TensorFlow（启用长路径后）
pip install tensorflow
```

### 使用 requirements.txt

```bash
# 基础安装（不包含 TensorFlow）
pip install -r requirements.txt

# 完整安装（需要启用长路径）
# 编辑 requirements.txt，取消 tensorflow 行的注释
# 然后运行：
pip install -r requirements.txt
```

---

## ✅ 验证安装

### 检查 Plotly
```bash
python -c "import plotly; print(f'Plotly version: {plotly.__version__}')"
```

### 检查 TensorFlow（如果已安装）
```bash
python -c "import tensorflow; print(f'TensorFlow version: {tensorflow.__version__}')"
```

### 检查 Tushare
```bash
python -c "import tushare; print('Tushare installed successfully')"
```

---

## 🚀 当前项目状态

### 已安装
- ✅ pandas
- ✅ numpy
- ✅ tushare
- ✅ scikit-learn
- ✅ matplotlib
- ✅ seaborn
- ✅ plotly
- ✅ requests
- ✅ beautifulsoup4

### 可选
- ⚠️ tensorflow（需要启用 Windows 长路径）

---

## 📝 使用说明

### 不使用 TensorFlow

```bash
# 运行主程序（不需要 TensorFlow）
python main.py

# 运行策略演示
python run_strategy_demo.py

# 运行股票推荐
python run_stock_recommender.py

# 更新价格数据
python update_prices.py
```

### 使用 TensorFlow

如果成功安装 TensorFlow，可以使用 ML 预测功能：

```python
from models.stock_predictor import StockPredictor

predictor = StockPredictor()
predictor.train_lstm_model(stock_data)
```

---

## 🔧 故障排除

### 问题 1: pip 下载超时

**解决**: 使用国内镜像
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple tensorflow
```

### 问题 2: 磁盘空间不足

**解决**: TensorFlow 需要约 5GB 空间
- 清理磁盘空间
- 或使用 tensorflow-cpu 版本（较小）

### 问题 3: Python 版本不兼容

**解决**: TensorFlow 2.20 支持 Python 3.8-3.11
```bash
python --version  # 检查 Python 版本
```

---

## 📖 相关文档

- [README.md](README.md) - 项目总览
- [TUSHARE_SETUP.md](TUSHARE_SETUP.md) - Tushare 配置指南
- [PRICE_UPDATE_TUSHARE.md](PRICE_UPDATE_TUSHARE.md) - 价格更新说明

---

*最后更新：2026 年 3 月*
