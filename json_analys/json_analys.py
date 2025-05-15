import json
import os
import argparse
from collections import defaultdict

def analyze_json_structure(data, path="", result=None, level=0):
    """
    递归分析JSON结构，记录每个字段的路径、类型和层级
    
    参数:
    - data: 要分析的JSON数据
    - path: 当前字段的路径
    - result: 存储分析结果的字典
    - level: 当前层级深度
    
    返回:
    - 包含分析结果的字典
    """
    if result is None:
        result = {
            "fields": [],
            "types": defaultdict(int),
            "max_level": 0
        }
    
    # 更新最大层级
    result["max_level"] = max(result["max_level"], level)
    
    if isinstance(data, dict):
        # 处理字典类型
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            field_info = {
                "path": current_path,
                "type": type(value).__name__,
                "level": level
            }
            result["fields"].append(field_info)
            result["types"][type(value).__name__] += 1
            
            # 递归处理嵌套结构
            if isinstance(value, (dict, list)):
                analyze_json_structure(value, current_path, result, level + 1)
    
    elif isinstance(data, list):
        # 处理列表类型
        result["types"]["list"] += 1
        
        # 分析列表中的第一个元素作为示例（如果存在）
        if data:
            sample_item = data[0]
            sample_path = f"{path}[0]"
            field_info = {
                "path": sample_path,
                "type": type(sample_item).__name__,
                "level": level
            }
            result["fields"].append(field_info)
            
            # 递归处理嵌套结构
            if isinstance(sample_item, (dict, list)):
                analyze_json_structure(sample_item, sample_path, result, level + 1)
    
    return result

def generate_markdown_report(analysis_result, json_filename):
    """
    根据分析结果生成Markdown格式的报告
    
    参数:
    - analysis_result: 分析结果字典
    - json_filename: 原始JSON文件名
    
    返回:
    - Markdown格式的报告文本
    """
    # 提取文件名（不含路径和扩展名）
    base_filename = os.path.basename(json_filename)
    file_title = os.path.splitext(base_filename)[0]
    
    # 创建报告标题
    report = [
        f"# JSON结构分析报告: {file_title}",
        "",
        "## 数据类型统计",
        "",
        "| 数据类型 | 出现次数 |",
        "| -------- | -------- |"
    ]
    
    # 添加类型统计
    for type_name, count in analysis_result["types"].items():
        report.append(f"| {type_name} | {count} |")
    
    # 添加字段层级结构
    report.extend([
        "",
        "## 字段层级结构",
        "",
        "| 层级 | 字段路径 | 数据类型 |",
        "|--|--|--|"
    ])
    
    # 按层级排序字段
    sorted_fields = sorted(analysis_result["fields"], key=lambda x: (x["level"], x["path"]))
    
    # 添加字段信息
    for field in sorted_fields:
        report.append(f"| {field['level']} | {field['path']} | {field['type']} |")
    
    # 添加树形结构可视化
    report.extend([
        "",
        "## 树形结构可视化",
        "",
        "```",
    ])
    
    # 构建树形结构
    tree_structure = generate_tree_structure(sorted_fields)
    report.extend(tree_structure)
    
    report.append("```")
    
    return "\n".join(report)

def generate_tree_structure(sorted_fields):
    """
    生成树形结构的文本表示
    
    参数:
    - sorted_fields: 按层级排序的字段列表
    
    返回:
    - 树形结构的文本行列表
    """
    tree_lines = []
    
    for field in sorted_fields:
        indent = "  " * field["level"]
        path_parts = field["path"].split(".")
        current_name = path_parts[-1]
        tree_lines.append(f"{indent}├── {current_name} ({field['type']})")
    
    return tree_lines

def analys_json(input_file, output_dir):
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 从输入文件名生成输出文件名
    base_filename = os.path.basename(input_file)
    file_title = os.path.splitext(base_filename)[0]
    output_file = os.path.join(output_dir, f"{file_title}_analysis.md")
    
    # 读取JSON文件
    with open(input_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            print(f"成功加载JSON文件: {input_file}")
            
            # 分析JSON结构
            analysis_result = analyze_json_structure(data)
            print(f"分析完成，共发现 {len(analysis_result['fields'])} 个字段，最大层级深度: {analysis_result['max_level']}")
            
            # 生成Markdown报告
            markdown_report = generate_markdown_report(analysis_result, input_file)
            
            # 保存报告到文件
            with open(output_file, "w", encoding="utf-8") as out_f:
                out_f.write(markdown_report)
            
            print(f"分析报告已保存到: {output_file}")
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
        except Exception as e:
            print(f"处理过程中发生错误: {e}")

def analys_json_folder(input_folder, output_dir):
    """
    分析指定文件夹中所有JSON文件的结构，判断字段层级关系和字段格式是否一致
    
    参数:
    - input_folder: 输入JSON文件所在的文件夹路径
    - output_dir: 输出分析报告的文件夹路径
    """
    import glob
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有JSON文件
    json_files = glob.glob(os.path.join(input_folder, "*.json"))
    if not json_files:
        print(f"在 {input_folder} 中未找到JSON文件")
        return None
    
    print(f"在 {input_folder} 中找到 {len(json_files)} 个JSON文件")
    
    # 存储所有文件的字段信息
    # 结构: {字段路径: {类型: [出现的文件列表]}}
    field_types = {}
    
    # 记录所有文件名
    all_files = []
    
    # 分析每个文件
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 分析JSON结构
            file_result = analyze_json_structure(data)
            
            # 提取文件名（不含路径和扩展名）
            base_filename = os.path.basename(json_file)
            file_title = os.path.splitext(base_filename)[0]
            all_files.append(file_title)
            
            # 记录每个字段的类型和出现的文件
            for field_info in file_result["fields"]:
                field_path = field_info["path"]
                field_type = field_info["type"]
                
                if field_path not in field_types:
                    field_types[field_path] = {}
                
                if field_type not in field_types[field_path]:
                    field_types[field_path][field_type] = []
                
                field_types[field_path][field_type].append(file_title)
            
            print(f"已分析文件: {json_file}")
            
        except Exception as e:
            print(f"处理文件 {json_file} 时出错: {e}")
    
    # 生成字段一致性分析报告
    consistency_report = generate_field_consistency_report(field_types, all_files)
    
    # 保存字段一致性分析报告
    consistency_file = os.path.join(output_dir, "field_consistency_analysis.md")
    with open(consistency_file, "w", encoding="utf-8") as f:
        f.write(consistency_report)
    
    print(f"字段一致性分析报告已保存到: {consistency_file}")

def generate_field_consistency_report(field_types, all_files):
    """
    生成字段一致性分析报告
    
    参数:
    - field_types: 包含所有字段类型信息的字典 {字段路径: {类型: [出现的文件列表]}}
    - all_files: 所有分析的文件名列表
    
    返回:
    - Markdown格式的字段一致性分析报告
    """
    if not field_types:
        return "# JSON字段一致性分析\n\n未找到有效的字段信息。"
    
    total_files = len(all_files)
    
    # 计算不一致字段数量
    inconsistent_fields = [path for path, types in field_types.items() if len(types) > 1]
    
    # 生成报告
    report = [
        "# JSON字段一致性分析",
        "",
        f"## 分析结果概述",
        "",
        f"- 总文件数: {total_files}",
        f"- 总字段数: {len(field_types)}",
        f"- 格式一致的字段数: {len(field_types) - len(inconsistent_fields)}",
        f"- 格式不一致的字段数: {len(inconsistent_fields)}",
        "",
        "## 所有字段及其格式",
        "",
        "| 层级 | 字段路径 | 数据类型 | 是否一致 | 出现的文件 |",
        "| ---- | -------- | -------- | -------- | ---------- |"
    ]
    
    # 按字段路径排序
    sorted_fields = sorted(field_types.keys())
    
    # 添加字段信息
    for field_path in sorted_fields:
        types = field_types[field_path]
        is_consistent = len(types) == 1
        
        # 计算字段层级
        # 对于根级字段，层级为0；对于每个点号，层级加1
        # 对于数组元素（如path[0]），不增加层级
        level = field_path.count(".")
        if "[" in field_path and "]" in field_path:
            # 数组元素的处理，不增加额外层级
            pass
        
        # 获取类型信息
        type_info = ", ".join(types.keys())
        
        # 获取文件信息
        if is_consistent:
            # 对于一致的字段，显示文件列表或"所有文件"
            files = list(types.values())[0]
            if len(files) == total_files:
                file_info = f"所有{total_files}个文件"
            else:
                if len(files) > 2:
                    file_info = ", ".join(files[:2]) + f" 等{len(files)}个文件"
                else:
                    file_info = ", ".join(files) + f" 等{len(files)}个文件"
        else:
            # 对于不一致的字段，分开显示每种类型对应的文件
            file_info_parts = []
            for type_name, files in types.items():
                if len(files) > 2:
                    file_example = ", ".join(files[:2]) + f" 等{len(files)}个文件"
                else:
                    file_example = ", ".join(files) + f" 等{len(files)}个文件"
                file_info_parts.append(f"{type_name}: {file_example}")
            file_info = "<br>".join(file_info_parts)
        
        report.append(f"| {level} | {field_path} | {type_info} | {'是' if is_consistent else '否'} | {file_info} |")
    
    # 添加不一致字段的详细信息
    if inconsistent_fields:
        report.extend([
            "",
            "## 格式不一致的字段详情",
            ""
        ])
        
        for field_path in inconsistent_fields:
            types = field_types[field_path]
            
            # 计算字段层级
            level = field_path.count(".")
            
            report.extend([
                f"### 字段: {field_path} (层级: {level})",
                "",
                "| 数据类型 | 出现的文件 |",
                "| -------- | ---------- |"
            ])
            
            for type_name, files in types.items():
                # 显示该类型下的所有文件
                file_list = ", ".join(files)
                report.append(f"| {type_name} | {file_list} |")
            
            report.append("")
    
    return "\n".join(report)

def analyze_consistency(all_results):
    """
    分析多个JSON文件结构的一致性
    
    参数:
    - all_results: 包含所有文件分析结果的字典
    
    返回:
    - Markdown格式的一致性分析报告
    """
    if not all_results:
        return "# JSON结构一致性分析\n\n未找到有效的分析结果。"
    
    # 提取所有文件的最大层级
    max_levels = {file: result["max_level"] for file, result in all_results.items()}
    
    # 检查层级是否一致
    is_level_consistent = len(set(max_levels.values())) == 1
    consistent_level = list(max_levels.values())[0] if is_level_consistent else None
    
    # 提取所有文件的数据类型统计
    type_stats = {}
    for file, result in all_results.items():
        type_stats[file] = dict(result["types"])
    
    # 检查数据类型是否一致
    all_types = set()
    for types in type_stats.values():
        all_types.update(types.keys())
    
    type_consistency = {type_name: True for type_name in all_types}
    type_counts = {type_name: {} for type_name in all_types}
    
    for file, types in type_stats.items():
        for type_name in all_types:
            count = types.get(type_name, 0)
            type_counts[type_name][file] = count
    
    for type_name, counts in type_counts.items():
        if len(set(counts.values())) > 1:
            type_consistency[type_name] = False
    
    # 生成一致性报告
    report = [
        "# JSON结构一致性分析",
        "",
        f"## 分析的文件数量: {len(all_results)}",
        "",
        "## 层级一致性",
        "",
        f"层级是否一致: {'是' if is_level_consistent else '否'}",
        ""
    ]
    
    if is_level_consistent:
        report.append(f"所有文件的最大层级深度: {consistent_level}")
    else:
        report.append("各文件的最大层级深度:")
        report.append("")
        report.append("| 文件 | 最大层级 |")
        report.append("| ---- | -------- |")
        for file, level in max_levels.items():
            report.append(f"| {file} | {level} |")
    
    report.extend([
        "",
        "## 数据类型一致性",
        ""
    ])
    
    # 添加数据类型一致性表格
    report.append("| 数据类型 | 是否一致 | 详情 |")
    report.append("| -------- | -------- | ---- |")
    
    for type_name in sorted(all_types):
        is_consistent = type_consistency[type_name]
        if is_consistent:
            count = list(type_counts[type_name].values())[0]
            report.append(f"| {type_name} | 是 | 所有文件中出现 {count} 次 |")
        else:
            details = ", ".join([f"{file}: {count}" for file, count in type_counts[type_name].items()])
            report.append(f"| {type_name} | 否 | {details} |")
    
    # 添加总体一致性结论
    report.extend([
        "",
        "## 总体结论",
        "",
        f"JSON结构{'完全一致' if is_level_consistent and all(type_consistency.values()) else '不一致'}。",
        "",
        "### 不一致项:",
        ""
    ])
    
    if not is_level_consistent:
        report.append("- 层级深度不一致")
    
    for type_name, is_consistent in type_consistency.items():
        if not is_consistent:
            report.append(f"- 数据类型 '{type_name}' 的出现次数不一致")
    
    return "\n".join(report)

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='JSON结构分析工具')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', help='要分析的单个JSON文件路径')
    group.add_argument('--folder', help='包含多个JSON文件的文件夹路径')
    parser.add_argument('--output', default='./analysis_results', help='分析报告输出目录，默认为"./analysis_results"')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 根据参数执行相应的分析
    if args.file:
        print(f"开始分析单个JSON文件: {args.file}")
        analys_json(args.file, args.output)
    elif args.folder:
        print(f"开始分析文件夹中的所有JSON文件: {args.folder}")
        analys_json_folder(args.folder, args.output)
    
    print("分析完成！")
    
