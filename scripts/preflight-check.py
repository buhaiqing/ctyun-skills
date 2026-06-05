#!/usr/bin/env python3
"""
Intelligent pre-flight check for CTyun Skills Farm environment.

This script performs comprehensive checks to ensure the environment is
properly configured for CLI-first policy execution. It's designed to be
ops-friendly with clear diagnostics and actionable suggestions.

Usage:
  python3 scripts/preflight-check.py [--verbose] [--fix]

Features:
  1. Checks Python version compatibility
  2. Verifies ctyun CLI availability (ctyun or ctyun-cli)
  3. Validates credential configuration
  4. Tests basic CLI functionality
  5. Provides intelligent fixes where possible
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class PreflightCheck:
    def __init__(self, verbose: bool = False, fix: bool = False):
        self.verbose = verbose
        self.fix = fix
        self.checks = []
        self.errors = []
        self.warnings = []
        self.symlink_created = False
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with level prefix."""
        if level == "ERROR":
            print(f"❌ {message}", file=sys.stderr)
        elif level == "WARNING":
            print(f"⚠️  {message}", file=sys.stderr)
        elif level == "SUCCESS":
            print(f"✅ {message}")
        elif self.verbose:
            print(f"ℹ️  {message}")
    
    def run_command(self, cmd: List[str], check: bool = True, **kwargs) -> Tuple[int, str, str]:
        """Run a command and return (exit_code, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                **kwargs
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return 1, "", str(e)
    
    def check_python_version(self):
        """Check Python version compatibility (3.10+ recommended)."""
        self.log("Checking Python version...")
        major, minor = sys.version_info[:2]
        
        if major == 3 and minor >= 10:
            self.log(f"Python {major}.{minor} is compatible", "SUCCESS")
            self.checks.append(("python_version", True, f"Python {major}.{minor}"))
        elif major == 3 and minor < 10:
            self.log(f"Python {major}.{minor} is below recommended 3.10+", "WARNING")
            self.warnings.append(f"Python {major}.{minor} is below recommended 3.10+")
            self.checks.append(("python_version", True, f"Python {major}.{minor} (warning)"))
        else:
            self.log(f"Python {major}.{minor} is not compatible", "ERROR")
            self.errors.append(f"Python {major}.{minor} is not compatible")
            self.checks.append(("python_version", False, f"Python {major}.{minor}"))
    
    def check_ctyun_cli(self):
        """Check if ctyun CLI is available (ctyun or ctyun-cli)."""
        self.log("Checking ctyun CLI availability...")
        
        # Check for ctyun command
        exit_code, stdout, stderr = self.run_command(["which", "ctyun"], check=False)
        if exit_code == 0:
            self.log(f"ctyun command found: {stdout}", "SUCCESS")
            self.checks.append(("ctyun_cli", True, f"ctyun at {stdout}"))
            return True
        
        # Check for ctyun-cli command
        exit_code, stdout, stderr = self.run_command(["which", "ctyun-cli"], check=False)
        if exit_code == 0:
            self.log(f"ctyun-cli command found: {stdout}", "SUCCESS")
            self.log("Note: Found ctyun-cli but not ctyun. Creating symlink for compatibility...")
            
            if self.fix:
                # Create symlink
                cli_path = Path(stdout)
                symlink_path = cli_path.parent / "ctyun"
                try:
                    if symlink_path.exists():
                        symlink_path.unlink()
                    symlink_path.symlink_to(cli_path.name)
                    self.log(f"Created symlink: {symlink_path} -> {cli_path.name}", "SUCCESS")
                    self.symlink_created = True
                    self.checks.append(("ctyun_cli", True, f"ctyun-cli at {stdout} (symlink created)"))
                    return True
                except Exception as e:
                    self.log(f"Failed to create symlink: {e}", "ERROR")
                    self.errors.append(f"Failed to create ctyun symlink: {e}")
                    self.checks.append(("ctyun_cli", True, f"ctyun-cli at {stdout} (no symlink)"))
                    return True
            else:
                self.log("Run with --fix to create ctyun symlink automatically", "WARNING")
                self.warnings.append("ctyun-cli found but ctyun symlink missing")
                self.checks.append(("ctyun_cli", True, f"ctyun-cli at {stdout} (no symlink)"))
                return True
        
        self.log("ctyun CLI not found in PATH", "ERROR")
        self.errors.append("ctyun CLI not found in PATH")
        self.checks.append(("ctyun_cli", False, "not found"))
        return False
    
    def check_ctyun_version(self):
        """Check ctyun CLI version."""
        self.log("Checking ctyun version...")
        
        # Try ctyun first, then ctyun-cli
        for cmd in ["ctyun", "ctyun-cli"]:
            exit_code, stdout, stderr = self.run_command([cmd, "--help"], check=False)
            if exit_code == 0:
                # Try to get version from help
                version_match = None
                for line in stdout.split('\n'):
                    if 'version' in line.lower():
                        version_match = line.strip()
                        break
                
                if version_match:
                    self.log(f"ctyun CLI: {version_match}", "SUCCESS")
                    self.checks.append(("ctyun_version", True, version_match))
                else:
                    self.log("ctyun CLI works (version unknown)", "SUCCESS")
                    self.checks.append(("ctyun_version", True, "unknown version"))
                return True
        
        self.log("Could not determine ctyun version", "WARNING")
        self.warnings.append("Could not determine ctyun version")
        self.checks.append(("ctyun_version", False, "unknown"))
        return False
    
    def check_credentials(self):
        """Check credential configuration."""
        self.log("Checking credential configuration...")
        
        # Check environment variables
        env_vars = ["CTYUN_ACCESS_KEY", "CTYUN_SECRET_KEY"]
        env_found = []
        env_missing = []
        
        for var in env_vars:
            if var in os.environ and os.environ[var]:
                env_found.append(var)
                # Mask secret key in logs
                if var == "CTYUN_SECRET_KEY":
                    self.log(f"{var}: [MASKED]", "SUCCESS")
                else:
                    self.log(f"{var}: set", "SUCCESS")
            else:
                env_missing.append(var)
                self.log(f"{var}: not set", "WARNING")
        
        # Check .env file
        env_file = Path(".env")
        if env_file.exists():
            self.log(".env file exists", "SUCCESS")
            self.checks.append(("credentials_env_file", True, ".env exists"))
        else:
            self.log(".env file not found", "WARNING")
            self.warnings.append(".env file not found")
            self.checks.append(("credentials_env_file", False, "not found"))
        
        # Check ~/.ctyun/config
        ctyun_config = Path.home() / ".ctyun" / "config"
        if ctyun_config.exists():
            self.log(f"~/.ctyun/config exists", "SUCCESS")
            self.checks.append(("credentials_cli_config", True, "~/.ctyun/config exists"))
        else:
            self.log("~/.ctyun/config not found", "WARNING")
            self.warnings.append("~/.ctyun/config not found")
            self.checks.append(("credentials_cli_config", False, "not found"))
        
        if len(env_found) == 2:
            self.checks.append(("credentials", True, "environment variables set"))
            return True
        elif env_file.exists() or ctyun_config.exists():
            self.checks.append(("credentials", True, "config files exist"))
            return True
        else:
            self.log("No credentials configured", "ERROR")
            self.errors.append("No credentials configured")
            self.checks.append(("credentials", False, "not configured"))
            return False
    
    def test_cli_command(self):
        """Test a simple CLI command to verify functionality."""
        self.log("Testing basic CLI functionality...")
        
        # Try a simple command that doesn't require auth
        for cmd_name in ["ctyun", "ctyun-cli"]:
            exit_code, stdout, stderr = self.run_command([cmd_name, "--help"], check=False)
            if exit_code == 0:
                self.log(f"{cmd_name} --help works", "SUCCESS")
                self.checks.append(("cli_test", True, f"{cmd_name} --help"))
                return True
        
        self.log("Basic CLI test failed", "ERROR")
        self.errors.append("Basic CLI test failed")
        self.checks.append(("cli_test", False, "failed"))
        return False
    
    def check_uv(self):
        """Check if uv is available (recommended package manager)."""
        self.log("Checking uv availability...")
        
        exit_code, stdout, stderr = self.run_command(["uv", "--version"], check=False)
        if exit_code == 0:
            self.log(f"uv found: {stdout}", "SUCCESS")
            self.checks.append(("uv", True, stdout))
            return True
        
        self.log("uv not found (recommended for package management)", "WARNING")
        self.warnings.append("uv not found")
        self.checks.append(("uv", False, "not found"))
        return False
    
    def generate_report(self):
        """Generate a comprehensive report."""
        print("\n" + "="*60)
        print("CTYUN SKILLS FARM - PREFLIGHT CHECK REPORT")
        print("="*60)
        
        # Summary
        total_checks = len(self.checks)
        passed_checks = sum(1 for _, passed, _ in self.checks if passed)
        
        print(f"\n📊 Summary: {passed_checks}/{total_checks} checks passed")
        
        # Detailed checks
        print("\n🔍 Detailed Checks:")
        for name, passed, details in self.checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}: {details}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Errors
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        
        if not self.checks[0][1]:  # python_version failed
            print("  • Install Python 3.10+ (recommended for CTyun compatibility)")
        
        if not self.checks[1][1]:  # ctyun_cli failed
            print("  • Install ctyun-cli: pip install ctyun-cli")
            print("  • Or use uv: uv pip install ctyun-cli")
        
        if "No credentials configured" in self.errors:
            print("  • Configure credentials:")
            print("    1. Copy .env.example to .env and fill in credentials")
            print("    2. Or set CTYUN_ACCESS_KEY and CTYUN_SECRET_KEY environment variables")
            print("    3. Or configure ~/.ctyun/config for CLI")
        
        if self.symlink_created:
            print("  • Created ctyun symlink for backward compatibility")
        
        if self.warnings and "ctyun-cli found but ctyun symlink missing" in self.warnings:
            print("  • Run with --fix to create ctyun symlink automatically")
        
        # Final status
        print("\n" + "="*60)
        if self.errors:
            print("❌ PREFLIGHT FAILED - Fix errors above")
            return False
        elif self.warnings:
            print("⚠️  PREFLIGHT WITH WARNINGS - Review warnings above")
            return True
        else:
            print("✅ PREFLIGHT PASSED - Environment is ready")
            return True
    
    def run_all(self):
        """Run all checks."""
        self.check_python_version()
        self.check_uv()
        self.check_ctyun_cli()
        self.check_ctyun_version()
        self.check_credentials()
        self.test_cli_command()
        
        return self.generate_report()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CTyun Skills Farm preflight check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fix", "-f", action="store_true", help="Attempt to fix issues automatically")
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    checker = PreflightCheck(verbose=args.verbose, fix=args.fix)
    success = checker.run_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()