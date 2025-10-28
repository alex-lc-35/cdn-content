""" markdoxn_transformer """
import markdown

def convert_md_file_to_html(md_path, html_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
