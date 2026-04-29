"""
Jira Deep Analysis CLI - Test Suite

Run basic tests to verify components work correctly.
"""

def test_config_loading():
    from backend.services.cli.config import load_config
    from pathlib import Path

    config = load_config(Path('config.yaml'))
    assert config.jira.server_url
    assert config.jira.project_keys
    print("Config loading works")

def test_index_tracker():
    from backend.services.cli.index_tracker import IndexTracker
    from pathlib import Path

    tracker = IndexTracker(Path('./data/test_cache.json'))
    tracker.mark_indexed('test', 'item1', {'meta': 'data'})
    assert tracker.is_indexed('test', 'item1')
    assert 'item1' in tracker.get_indexed_items('test')
    tracker.clear()
    print("IndexTracker works")

def test_output_formatter():
    from backend.services.cli.output_formatter import OutputFormatter
    from pathlib import Path

    formatter = OutputFormatter(Path('./test_output'))

    issue = {
        'key': 'TEST-1',
        'content': 'Test content',
        'metadata': {'status': 'Open', 'priority': 'High', 'assignee': 'User'}
    }

    result = formatter.save('TEST-1', issue, [], [], 'Test RCA')
    assert Path(result['markdown_path']).exists()
    assert Path(result['html_path']).exists()
    print("OutputFormatter works")

if __name__ == '__main__':
    import sys

    try:
        test_config_loading()
        test_index_tracker()
        test_output_formatter()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
