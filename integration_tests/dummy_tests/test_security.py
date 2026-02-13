
import os
import shutil
import subprocess
import sys
from pathlib import Path
import pytest

def _run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True)

@pytest.fixture
def minimal_allure_report(tmp_path):
    report_dir = tmp_path / "report"
    report_dir.mkdir()
    
    (report_dir / "index.html").write_text(
        '<html><head><script src="app.js"></script><link rel="stylesheet" href="styles.css"></head><body></body></html>',
        encoding="utf-8"
    )
    (report_dir / "app.js").write_text('console.log("app");', encoding="utf-8")
    (report_dir / "styles.css").write_text('body { color: red; }', encoding="utf-8")
    
    data_dir = report_dir / "data"
    data_dir.mkdir()
    
    return report_dir

def test_disable_tags_escaping_prevents_xss(minimal_allure_report, tmp_path):
    """
    Test that even when disable_tags_escaping is True, </script> tags in content
    are escaped (as unicode escapes) to prevent breaking the parent script tag.
    """
    
    # Create a file that triggers the issue
    evil_content = 'Some content with </script> tag inside.'
    (minimal_allure_report / "data" / "evil.txt").write_text(evil_content, encoding="utf-8")
    
    # Run allure-combine with --disable-tags-escaping
    cmd = _run([sys.executable, "-m", "allure_combine.combine", str(minimal_allure_report), "--disable-tags-escaping"])
    
    assert cmd.returncode == 0, cmd.stdout + cmd.stderr
    
    complete_html = minimal_allure_report / "complete.html"
    assert complete_html.exists()
    
    content = complete_html.read_text(encoding="utf-8")
    
    # We expect the literal </script> to NOT be present in the JS string definition
    # because it should be escaped as \u003c/script\u003e
    snippet_unescaped = '"data/evil.txt": "Some content with </script> tag inside."'
    snippet_escaped = r'"data/evil.txt": "Some content with \u003c/script\u003e tag inside."'
    
    assert snippet_unescaped not in content, "Found unescaped </script> tag in the output!"
    assert snippet_escaped in content, "Did not find expected escaped snippet."

def test_disable_tags_escaping_preserves_html_semantics(minimal_allure_report):
    """
    Test that disable_tags_escaping=True preserves < and > as unicode escapes
    which evaluate to correct characters in JS, effectively disabling HTML entity escaping.
    """
    
    html_content = "<div><b>Bold</b></div>"
    (minimal_allure_report / "data" / "content.txt").write_text(html_content, encoding="utf-8")
    
    cmd = _run([sys.executable, "-m", "allure_combine.combine", str(minimal_allure_report), "--disable-tags-escaping"])
    assert cmd.returncode == 0
    
    content = (minimal_allure_report / "complete.html").read_text(encoding="utf-8")
    
    # Should use unicode escapes
    expected = r'"data/content.txt": "\u003cdiv\u003e\u003cb\u003eBold\u003c/b\u003e\u003c/div\u003e"'
    assert expected in content

def test_default_behavior_uses_entities(minimal_allure_report):
    """
    Verify default behavior uses &lt; and &gt;
    """
    html_content = "<div><b>Bold</b></div>"
    (minimal_allure_report / "data" / "content.txt").write_text(html_content, encoding="utf-8")
    
    cmd = _run([sys.executable, "-m", "allure_combine.combine", str(minimal_allure_report)])
    assert cmd.returncode == 0
    
    content = (minimal_allure_report / "complete.html").read_text(encoding="utf-8")
    
    # Should use HTML entities
    expected = '"data/content.txt": "&lt;div&gt;&lt;b&gt;Bold&lt;/b&gt;&lt;/div&gt;"'
    assert expected in content
