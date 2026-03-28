import markdown


def create_markdown_content(content: str):
    md = markdown.Markdown(extensions=["fenced_code", "tables", "nl2br"])
    markdown_content = md.convert(content)
    return markdown_content
