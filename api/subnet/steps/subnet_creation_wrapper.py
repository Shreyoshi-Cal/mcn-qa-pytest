"""
subnet_creation_wrapper.py
──────────────────────────
A thin orchestration layer that calls your existing **pytest-bdd**
test_subnet_creation.py scenario repeatedly, supplying a different CIDR block 
and auto-generated subnet/stack name each time.

How it works
────────────
1.  The wrapper receives:
      • `vpc_id`          - VPC ID where subnets will be created
      • `count`           - number of subnets to create (≤ len(cidr_blocks))
      • `cidr_blocks`     - list/tuple of CIDRs to use
2.  For every index i it
      • builds a unique subnet name  →  f"bulk-subnet-{timestamp}-{i:02d}"
      • builds a unique stack name   →  f"bulk-subnet-stack-{timestamp}-{i:02d}"
      • sets four **environment variables** expected by the BDD test:
            SUBNET_BULK_VPC_ID
            SUBNET_BULK_CIDR
            SUBNET_BULK_NAME
            SUBNET_BULK_STACK
      • invokes *pytest* in a subprocess, targeting the single
        "Successfully create a subnet" scenario inside
        `api/subnet/steps/test_subnet_creation.py`
3.  Captures stdout/stderr and return code so you see per-subnet results.
"""

from __future__ import annotations
import os, sys, subprocess, time, datetime
from pathlib import Path
from typing import Sequence

class SubnetBulkWrapper:
    """Run the pytest BDD subnet-creation scenario N times with new CIDRs."""

    def __init__(
        self,
        test_file: str = "api/subnet/steps/test_subnet_creation.py",
        python_exe: str | None = None,
    ):
        self.test_file = Path(test_file).resolve()
        if not self.test_file.exists():
            raise FileNotFoundError(self.test_file)
        self.python_exe = python_exe or sys.executable

    def create_subnets(self, vpc_id: str, count: int, cidr_blocks: Sequence[str]) -> None:
        if count < 1:
            raise ValueError("count must be positive")
        if count > len(cidr_blocks):
            raise ValueError("count cannot exceed number of CIDR blocks supplied")
        if not vpc_id.startswith("vpc-"):
            raise ValueError("vpc_id must start with 'vpc-'")

        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        for idx in range(count):
            subnet_name = f"bulk-subnet-{ts}-{idx:02d}"
            stack_name  = f"bulk-subnet-stack-{ts}-{idx:02d}"
            cidr        = cidr_blocks[idx]

            # Set environment variables for the pytest test to pick up
            env = os.environ.copy()
            env["SUBNET_BULK_VPC_ID"] = vpc_id
            env["SUBNET_BULK_CIDR"]   = cidr
            env["SUBNET_BULK_NAME"]   = subnet_name
            env["SUBNET_BULK_STACK"]  = stack_name
            #env["SUBNET_BULK_AZ"] = "us-east-1a"          # or any valid AZ


            print(f"\n  [{idx+1}/{count}] Creating subnet {subnet_name} ({cidr}) in VPC {vpc_id} …")

            cmd = [
                self.python_exe,
                "-m", "pytest",
                f"{self.test_file}::test_successfully_create_a_subnet",
                "-q",
            ]

            result = subprocess.run(cmd, env=env, text=True, capture_output=True)
            if result.returncode == 0:
                print(f" {subnet_name} created successfully\n")
            else:
                print(f"  {subnet_name} FAILED\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}\n")
            time.sleep(1)   # tiny delay, avoid server overload

# ──────────────────────────────────────────────────────────────────────────────
# If run as a script:
#   python subnet_creation_wrapper.py vpc-0123456789abcdef0 3 10.0.1.0/24 10.0.2.0/24 10.0.3.0/24
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python subnet_creation_wrapper.py <vpc_id> <count> <cidr1> [<cidr2> …]")
        sys.exit(1)

    vpc_id = sys.argv[1]
    cnt = int(sys.argv[2])
    cidrs = sys.argv[3:]
    wrapper = SubnetBulkWrapper()
    wrapper.create_subnets(vpc_id, cnt, cidrs)
