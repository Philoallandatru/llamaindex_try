"""Mock Jira server for testing CLI tool"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Mock Jira issues
MOCK_ISSUES = {
    "TEST-123": {
        "key": "TEST-123",
        "fields": {
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
            "status": {"name": "Open"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "John Doe"},
            "created": "2024-01-15T10:00:00.000+0000",
            "updated": "2024-01-16T14:30:00.000+0000",
            "issuetype": {"name": "Bug"},
            "project": {"key": "TEST"}
        }
    },
    "TEST-456": {
        "key": "TEST-456",
        "fields": {
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
            "status": {"name": "In Progress"},
            "priority": {"name": "Medium"},
            "assignee": {"displayName": "Jane Smith"},
            "created": "2024-01-10T09:00:00.000+0000",
            "updated": "2024-01-15T16:00:00.000+0000",
            "issuetype": {"name": "Bug"},
            "project": {"key": "TEST"}
        }
    },
    "TEST-789": {
        "key": "TEST-789",
        "fields": {
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
            "status": {"name": "To Do"},
            "priority": {"name": "Low"},
            "assignee": {"displayName": "Bob Wilson"},
            "created": "2024-01-05T11:00:00.000+0000",
            "updated": "2024-01-08T10:00:00.000+0000",
            "issuetype": {"name": "Feature"},
            "project": {"key": "TEST"}
        }
    }
}

@app.get("/rest/api/2/search")
async def search_issues(jql: str = ""):
    """Mock Jira search endpoint"""
    issues = []

    # Simple JQL parsing
    if "project = TEST" in jql:
        issues = [
            {
                "key": key,
                "fields": data["fields"]
            }
            for key, data in MOCK_ISSUES.items()
        ]
    elif "key =" in jql:
        # Extract key from JQL
        key = jql.split("key =")[-1].strip()
        if key in MOCK_ISSUES:
            issues = [{
                "key": key,
                "fields": MOCK_ISSUES[key]["fields"]
            }]

    return {
        "total": len(issues),
        "issues": issues
    }

@app.get("/rest/api/2/issue/{issue_key}")
async def get_issue(issue_key: str):
    """Mock get single issue endpoint"""
    if issue_key in MOCK_ISSUES:
        return MOCK_ISSUES[issue_key]
    return JSONResponse(status_code=404, content={"error": "Issue not found"})

@app.get("/")
async def root():
    return {"message": "Mock Jira Server", "available_issues": list(MOCK_ISSUES.keys())}

if __name__ == "__main__":
    print("Starting Mock Jira Server on http://localhost:8080")
    print(f"Available issues: {list(MOCK_ISSUES.keys())}")
    uvicorn.run(app, host="0.0.0.0", port=8080)
