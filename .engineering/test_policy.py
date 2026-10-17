"""Policy enforcement regression tests; product pack tests remain standard-library only."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("policy_checker", ROOT/".engineering/check.py")
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)

class PolicyRegression(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for path in (".engineering",".github/workflows"):
            shutil.copytree(ROOT/path,self.root/path,ignore=shutil.ignore_patterns("__pycache__"))
        for path in ("AGENTS.md","CLAUDE.md"):
            shutil.copyfile(ROOT/path,self.root/path)
    def change(self,old,new):
        path=self.root/".github/workflows/check.yml"
        path.write_text(path.read_text().replace(old,new))
    def test_compliant(self):
        self.assertEqual(checker.check(self.root),[])
    def test_nonblocking_job(self):
        self.change("  validate:","  validate:\n    continue-on-error: true")
        self.assertTrue(any("nonblocking" in e for e in checker.check(self.root)))
    def test_nonblocking_step(self):
        self.change("      - name: Tests","      - continue-on-error: true\n        name: Tests")
        self.assertTrue(any("nonblocking" in e for e in checker.check(self.root)))
    def test_missing_job(self):
        self.change("  validate:","  replacement:")
        self.assertTrue(any("missing required job" in e for e in checker.check(self.root)))
    def test_incomplete_aggregate(self):
        self.change("needs: [check, validate]","needs: [check]")
        self.assertTrue(any("aggregate" in e for e in checker.check(self.root)))
    def test_unbounded_timeout(self):
        self.change("timeout-minutes: 45","timeout-minutes: 0")
        self.assertTrue(any("timeout" in e for e in checker.check(self.root)))
    def test_malformed_yaml(self):
        (self.root/".github/workflows/check.yml").write_text("jobs: [broken")
        self.assertTrue(any("invalid workflow" in e for e in checker.check(self.root)))
if __name__=="__main__":unittest.main()
