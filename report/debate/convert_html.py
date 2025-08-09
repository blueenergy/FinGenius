import json

def dict_to_html(d, indent=0):
    html = ""
    indent_str = "  " * indent
    if isinstance(d, dict):
        html += f"{indent_str}<ul>\n"
        for k, v in d.items():
            html += f"{indent_str}  <li><b>{k}:</b> {dict_to_html(v, indent+2)}</li>\n"
        html += f"{indent_str}</ul>\n"
    elif isinstance(d, list):
        html += f"{indent_str}<ul>\n"
        for item in d:
            html += f"{indent_str}  <li>{dict_to_html(item, indent+2)}</li>\n"
        html += f"{indent_str}</ul>\n"
    else:
        html += f"{str(d)}"
    return html

def json_to_html(json_file, html_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>JSON Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            ul {{ list-style-type: none; }}
            li {{ margin: 4px 0; }}
            b {{ color: #1a237e; }}
        </style>
    </head>
    <body>
        <h2>JSON 分析报告可视化</h2>
        {dict_to_html(data)}
    </body>
    </html>
    """
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

# 用法示例
json_to_html('debate_002050_20250804_090550.json', 'debate_002050_20250804_090550.html')