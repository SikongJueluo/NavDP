"""Integration checks for wheel layout, isolated imports and legacy script imports."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="navdp-packaging-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.work = Path(cls.temporary.name)
        cls.target = cls.work / "site"
        cls.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", USE_TF="0")
        cls.env.pop("PYTHONPATH", None)
        cls.run_command(
            [
                "uv",
                "build",
                "--no-config",
                "--cache-dir",
                str(cls.work / "cache"),
                "--python",
                sys.executable,
                "--wheel",
                "--out-dir",
                str(cls.work / "dist"),
                str(ROOT),
            ]
        )
        (cls.wheel,) = (cls.work / "dist").glob("*.whl")
        cls.run_command(
            [
                "uv",
                "--no-config",
                "pip",
                "install",
                "--offline",
                "--no-cache",
                "--python",
                sys.executable,
                "--no-deps",
                "--target",
                str(cls.target),
                str(cls.wheel),
            ]
        )

    @classmethod
    def run_command(cls, command, *, cwd=None):
        result = subprocess.run(
            command,
            cwd=cwd or cls.work,
            env=cls.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode:
            raise AssertionError(result.stdout)
        return result.stdout

    def test_wheel_contents(self):
        with ZipFile(self.wheel) as wheel:
            names = set(wheel.namelist())
            self.assertIn("navdp_policy/__init__.py", names)
            self.assertIn("navdp_policy/policy_agent.py", names)
            self.assertIn("navdp_policy/depth_anything/LICENSE", names)
            self.assertIn("navdp_policy/depth_anything/depth_anything_v2/dpt.py", names)
            self.assertTrue(any(name.endswith("/licenses/LICENSE") for name in names))
            self.assertTrue(any(name.endswith("/licenses/NOTICE.md") for name in names))
            self.assertTrue(
                all(
                    name.startswith("navdp_policy/") or ".dist-info/" in name
                    for name in names
                )
            )
            self.assertFalse(any("navdp_server" in name for name in names))
            self.assertFalse(
                any(name.endswith((".ckpt", ".pth", ".pt")) for name in names)
            )

    def test_isolated_installed_import(self):
        script = """
import importlib.util
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
import navdp_policy
from navdp_policy.depth_anything.depth_anything_v2.dpt import DepthAnythingV2
assert Path(sys.argv[1]).resolve() in Path(navdp_policy.__file__).resolve().parents
assert navdp_policy.NavDP_Agent.__module__ == "navdp_policy.policy_agent"
assert DepthAnythingV2.__module__.startswith("navdp_policy.")
for name in ("policy_agent", "policy_network", "policy_backbone", "depth_anything"):
    assert importlib.util.find_spec(name) is None, name
"""
        self.run_command([sys.executable, "-I", "-c", script, str(self.target)])

    def test_legacy_script_import(self):
        script = """
from policy_agent import NavDP_Agent
from policy_network import NavDP_Policy
from policy_backbone import NavDP_RGBD_Backbone
assert NavDP_Agent.__module__ == "policy_agent"
assert NavDP_Policy.__module__ == "policy_network"
assert NavDP_RGBD_Backbone.__module__ == "policy_backbone"
"""
        self.run_command([sys.executable, "-c", script], cwd=ROOT / "baselines/navdp")


if __name__ == "__main__":
    unittest.main()
