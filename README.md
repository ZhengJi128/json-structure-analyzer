# JSON结构分析工具

## 项目简介

JSON结构分析工具是一个用于分析JSON文件结构的Python工具，它可以帮助用户理解JSON数据的结构、字段层级关系和数据类型分布。该工具支持单个JSON文件分析和多个JSON文件的结构一致性比较。

## 功能特点

- 递归分析JSON结构，识别所有字段的路径、类型和层级
- 生成详细的Markdown格式分析报告
- 支持树形结构可视化
- 支持多文件结构一致性分析
- 自动检测指定文件夹内所有json字段类型不一致的情况

## 安装方法

1. 克隆仓库到本地：

```bash
git clone https://github.com/yourusername/json-structure-analyzer.git
cd json-structure-analyzer
pip install -r requirements.txt
```

### 分析单个JSON文件

```bash
python json_analys/json_analys.py --file path/to/your/file.json --output output_dir
```


```bash
python json_analys/json_analys.py --folder path/to/json/folder --output output_dir
```
