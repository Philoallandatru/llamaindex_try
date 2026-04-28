"""Format analysis output as markdown and HTML"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime

class OutputFormatter:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(self, jira_key: str, issue: Dict, similar: List[Dict],
             docs: List[Dict], rca: str, output_path: Path = None) -> Dict:
        """Save analysis as markdown and HTML"""
        output_path = output_path or self.output_dir
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{jira_key}_{timestamp}"

        md_content = self._generate_markdown(jira_key, issue, similar, docs, rca)
        html_content = self._generate_html(jira_key, issue, similar, docs, rca)

        md_path = output_path / f"{base_name}.md"
        html_path = output_path / f"{base_name}.html"

        md_path.write_text(md_content, encoding="utf-8")
        html_path.write_text(html_content, encoding="utf-8")

        return {
            "markdown_path": str(md_path),
            "html_path": str(html_path)
        }

    def _generate_markdown(self, jira_key: str, issue: Dict,
                          similar: List[Dict], docs: List[Dict], rca: str) -> str:
        return f"""# Jira Deep Analysis: {jira_key}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Issue Details

{issue['content']}

### Metadata
- **Key:** {issue['key']}
- **Status:** {issue['metadata'].get('status', 'N/A')}
- **Priority:** {issue['metadata'].get('priority', 'N/A')}
- **Assignee:** {issue['metadata'].get('assignee', 'N/A')}

---

## Similar Issues ({len(similar)})

{self._format_similar_md(similar)}

---

## Relevant Documentation ({len(docs)})

{self._format_docs_md(docs)}

---

## Root Cause Analysis

{rca}

---

## Next Steps

- [ ] Review RCA findings
- [ ] Validate action items
- [ ] Execute verification steps
- [ ] Update Jira issue with findings

"""

    def _format_similar_md(self, similar: List[Dict]) -> str:
        if not similar:
            return "*No similar issues found*"

        lines = []
        for i, item in enumerate(similar, 1):
            key = item['metadata'].get('key', 'Unknown')
            score = item.get('score', 0)
            lines.append(f"### {i}. {key} (similarity: {score:.2f})")
            lines.append(f"{item['text'][:300]}...")
            lines.append("")
        return "\n".join(lines)

    def _format_docs_md(self, docs: List[Dict]) -> str:
        if not docs:
            return "*No relevant documentation found*"

        lines = []
        for i, doc in enumerate(docs, 1):
            source = doc['metadata'].get('source', 'Unknown')
            title = doc['metadata'].get('title', 'Untitled')
            score = doc.get('score', 0)
            lines.append(f"### {i}. [{source}] {title} (relevance: {score:.2f})")
            lines.append(f"{doc['text'][:300]}...")
            lines.append("")
        return "\n".join(lines)

    def _generate_html(self, jira_key: str, issue: Dict,
                      similar: List[Dict], docs: List[Dict], rca: str) -> str:
        md_content = self._generate_markdown(jira_key, issue, similar, docs, rca)

        # Simple markdown to HTML conversion
        html_body = md_content.replace("\n## ", "\n<h2>").replace("\n### ", "\n<h3>")
        html_body = html_body.replace("\n---\n", "\n<hr>\n")
        html_body = html_body.replace("**", "<strong>").replace("**", "</strong>")
        html_body = html_body.replace("*", "<em>").replace("*", "</em>")

        # Close tags properly
        html_body = html_body.replace("<h2>", "</section><section><h2>").replace("<h3>", "<h3>")
        html_body = html_body.replace("\n\n", "</p><p>")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis: {jira_key}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
        h1 {{ color: #0052CC; border-bottom: 3px solid #0052CC; padding-bottom: 10px; }}
        h2 {{ color: #172B4D; margin-top: 30px; border-bottom: 1px solid #DFE1E6; padding-bottom: 8px; }}
        h3 {{ color: #42526E; }}
        hr {{ border: none; border-top: 2px solid #DFE1E6; margin: 30px 0; }}
        section {{ margin: 20px 0; }}
        code {{ background: #F4F5F7; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #F4F5F7; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        .metadata {{ background: #DEEBFF; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .checkbox {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>Jira Deep Analysis: {jira_key}</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    {html_body}
</body>
</html>
"""
