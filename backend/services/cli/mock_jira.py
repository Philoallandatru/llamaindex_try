"""Simple mock Jira data loader for testing without real Jira API"""

from pathlib import Path
from typing import List
from llama_index.core import Document

class MockJiraLoader:
    """Mock Jira loader that returns test data"""

    MOCK_ISSUES = {
        "TEST-123": {
            "key": "TEST-123",
            "summary": "NVMe SSD performance degradation after firmware update",
            "description": """
After updating firmware from v3.2 to v3.3, we observed significant performance degradation:
- Sequential read dropped from 3500 MB/s to 2800 MB/s
- Random IOPS decreased by 25%
- Latency increased from 50us to 80us

Environment:
- NVMe SSD: Samsung 980 PRO
- PCIe Gen4 x4
- Firmware: v3.3 (PCI_Firmware_v3.3_20210120_NCB.pdf)
- OS: Ubuntu 22.04

Steps to reproduce:
1. Update firmware to v3.3
2. Run fio benchmark
3. Compare results with v3.2

Expected: Performance should remain stable or improve
Actual: 20-25% performance drop

Related specs:
- NVM Express Base Specification 2.1
- PCIe Base 5.0 specification
            """,
            "status": "Open",
            "priority": "High",
            "assignee": "John Doe"
        },
        "TEST-456": {
            "key": "TEST-456",
            "summary": "PCIe link training failure on cold boot",
            "description": """
PCIe device fails to enumerate on cold boot, requires warm reboot to detect.

Symptoms:
- Device not visible in lspci on cold boot
- Works fine after warm reboot
- Link training timeout in dmesg

Hardware:
- PCIe Gen4 NVMe SSD
- Motherboard: ASUS ROG with PCIe 5.0 support

Investigation needed:
- Check PCIe link training sequence per PCIe Base 5.0 spec
- Verify power sequencing timing
- Review firmware initialization code
            """,
            "status": "In Progress",
            "priority": "Medium",
            "assignee": "Jane Smith"
        },
        "TEST-789": {
            "key": "TEST-789",
            "summary": "Implement NVMe namespace management",
            "description": """
Add support for NVMe namespace management commands per NVMe 2.1 spec.

Requirements:
- Namespace creation/deletion
- Namespace attachment/detachment
- Multi-namespace support
- Namespace sharing

Reference: NVM-Express-Base-Specification-Revision-2.1 Section 5.15
            """,
            "status": "To Do",
            "priority": "Low",
            "assignee": "Bob Wilson"
        }
    }

    def load_issues(self, project_key: str = "TEST") -> List[Document]:
        """Load mock Jira issues as Documents"""
        docs = []

        for key, issue in self.MOCK_ISSUES.items():
            if issue["key"].startswith(project_key):
                text = f"""
Issue: {issue['key']}
Summary: {issue['summary']}
Status: {issue['status']}
Priority: {issue['priority']}
Assignee: {issue['assignee']}

Description:
{issue['description']}
"""
                doc = Document(
                    text=text.strip(),
                    metadata={
                        "key": issue["key"],
                        "summary": issue["summary"],
                        "status": issue["status"],
                        "priority": issue["priority"],
                        "assignee": issue["assignee"],
                        "source": "jira",
                        "source_type": "jira_issue"
                    }
                )
                docs.append(doc)

        return docs

    def get_issue(self, issue_key: str) -> dict:
        """Get single issue by key"""
        if issue_key in self.MOCK_ISSUES:
            issue = self.MOCK_ISSUES[issue_key]
            return {
                "key": issue_key,
                "content": f"""
Issue: {issue['key']}
Summary: {issue['summary']}
Status: {issue['status']}
Priority: {issue['priority']}
Assignee: {issue['assignee']}

Description:
{issue['description']}
""".strip(),
                "metadata": {
                    "key": issue_key,
                    "summary": issue["summary"],
                    "status": issue["status"],
                    "priority": issue["priority"],
                    "assignee": issue["assignee"]
                }
            }
        raise ValueError(f"Issue {issue_key} not found")
