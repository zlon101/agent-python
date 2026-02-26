import mammoth
from markdownify import markdownify as md
import os
import sys

# docx to md: https://github.com/microsoft/markitdown

def convert_docx_to_markdown(docx_path, output_path=None):
    """
    将 docx 文件转换为 markdown，并处理标题风格
    """
    
    # 1. 检查文件是否存在
    if not os.path.exists(docx_path):
        print(f"❌ 错误: 找不到文件 '{docx_path}'")
        return

    # 2. 确定输出路径
    if output_path is None:
        # 默认在同目录下生成同名 .md 文件
        output_path = os.path.splitext(docx_path)[0] + ".md"

    try:
        print(f"正在转换: {docx_path} ...")

        # 3. 使用 mammoth 将 docx 转换为 HTML
        # mammoth 会尽量保留语义（如将 Word 的标题样式转为 <h1> 等）
        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value
            messages = result.messages # 警告信息

        # 4. 使用 markdownify 将 HTML 转换为 Markdown
        # heading_style="ATX" 强制使用 # 符号作为标题，而不是下划线
        # strip=['a'] 如果你想去除链接，可以加上这个参数
        markdown_content = md(html_content, heading_style="ATX")

        # 5. 写入 Markdown 文件
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)
        
        print(f"✅ 转换成功: {output_path}")

        # 如果有警告（例如图片转换问题），打印出来
        if messages:
            for message in messages:
                print(f"   ⚠️ 警告: {message.message}")

    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")

# --- 主程序入口 ---
if __name__ == "__main__":
    # 你可以直接在这里修改文件名运行
    # input_file = "你的文档.docx"
    # convert_docx_to_markdown(input_file)

    # 或者支持命令行拖拽文件运行
    if len(sys.argv) > 1:
        for file_path in sys.argv[1:]:
            if file_path.endswith(".docx"):
                convert_docx_to_markdown(file_path)
            else:
                print(f"跳过非 docx 文件: {file_path}")
    else:
        print("请将 .docx 文件拖放到此脚本上，或在代码中指定文件路径。")