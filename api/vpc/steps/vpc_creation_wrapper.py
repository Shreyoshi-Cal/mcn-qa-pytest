"""
vpc_creation_wrapper.py
───────────────────────
A thin orchestration layer that calls your existing **pytest-bdd**
test_vpc_creation.py scenario repeatedly, supplying a differentCIDR block and an auto-generated VPC / stack name each time.

How it works
────────────
1.  The wrapper receives:
      • `count`           number of VPCs to create (≤ len(cidr_blocks))
      • `cidr_blocks`     list/tuple of CIDRs to use
2.  For every index i it
      • builds a unique VPC name  →  f"bulk-vpc-{timestamp}-{i:02d}"
      • builds a unique stack name→  f"bulk-stack-{timestamp}-{i:02d}"
      • sets three **environment variables** expected by the BDD test:
            VPC_BULK_CIDR
            VPC_BULK_NAME
            VPC_BULK_STACK
      • invokes *pytest* in a subprocess, targeting the single
        “Successfully create a VPC …” scenario inside
        `api/vpc/steps/test_vpc_creation.py`
3.  Captures stdout/stderr and return code so you see per-VPC results.
"""

from __future__ import annotations
import os
import sys
import subprocess
import time
import datetime
from pathlib import Path
from typing import Sequence
import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,                      # show INFO and above
    format="%(asctime)s [%(levelname)-5s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class VPCBulkWrapper:
    """Run the pytest BDD VPC-creation scenario N times with new CIDRs."""

    def __init__(
        self,
        test_file: str = "api/vpc/steps/test_vpc_creation.py",
        python_exe: str | None = None,
    ):
        self.test_file = Path(test_file).resolve()
        if not self.test_file.exists():
            raise FileNotFoundError(self.test_file)
        self.python_exe = python_exe or sys.executable

    def create_vpcs(self, count: int, cidr_blocks: Sequence[str]) -> None:
        if count < 1:
            raise ValueError("count must be positive")
        if count > len(cidr_blocks):
            raise ValueError("count cannot exceed number of CIDR blocks supplied")

        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        for idx in range(count):
            vpc_name = f"bulk-vpc-{ts}-{idx:02d}"
            stack_name = f"bulk-stack-{ts}-{idx:02d}"
            cidr = cidr_blocks[idx]

            env = os.environ.copy()
            env["VPC_BULK_CIDR"] = cidr
            env["VPC_BULK_NAME"] = vpc_name
            env["VPC_BULK_STACK"] = stack_name

            logger.info("[%d/%d] Creating VPC %s (%s)", idx + 1, count, vpc_name, cidr)

            cmd = [
                self.python_exe,
                "-m", "pytest",
                f"{self.test_file}::test_successfully_create_a_vpc_on_aws_with_detailed_logging",
                "-q",
                "-s",
            ]

            result = subprocess.run(cmd, env=env, text=True, capture_output=True)
            if result.returncode == 0:
    
                vpc_id = None
                for line in result.stdout.splitlines():
                    if ("VPC_CREATED|ID=") in line:
            
                        parts = line.split("VPC_CREATED|ID=", 1)[1]
                        vpc_id = parts.split("|", 1)[0]
                        logger.info(" Extracted VPC ID: %s", vpc_id)
                        break
                                

                if not vpc_id:
                    logger.warning(" VPC ID not found in pytest output")
                

                logger.info("%s created successfully", vpc_name)
            else:
                logger.error(
        "%s FAILED\nstdout:\n%s\nstderr:\n%s",
        vpc_name,
        result.stdout,
        result.stderr,
    )
            time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.error("Usage: python vpc_creation_wrapper.py <count> <cidr1> [<cidr2> …]")
        sys.exit(1)

    cnt = int(sys.argv[1])
    cidrs = sys.argv[2:]
    wrapper = VPCBulkWrapper()
    wrapper.create_vpcs(cnt, cidrs)






'''from __future__ import annotations
import os, sys, subprocess, time, datetime
from pathlib import Path
from typing import Sequence



class VPCBulkWrapper:
    """Run the pytest BDD VPC-creation scenario N times with new CIDRs."""

    def __init__(
        self,
        test_file: str = "api/vpc/steps/test_vpc_creation.py",
        scenario_keyword: str = "Successfully create a VPC on AWS with detailed logging",
        python_exe: str | None = None,
    ):
        self.test_file = Path(test_file).resolve()
        if not self.test_file.exists():
            raise FileNotFoundError(self.test_file)
        self.scenario_keyword = scenario_keyword
        self.python_exe = python_exe or sys.executable      

   
    def create_vpcs(self, count: int, cidr_blocks: Sequence[str]) -> None:
        if count < 1:
            raise ValueError("count must be positive")
        if count > len(cidr_blocks):
            raise ValueError("count cannot exceed number of CIDR blocks supplied")

        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        for idx in range(count):
            vpc_name   = f"bulk-vpc-{ts}-{idx:02d}"
            stack_name = f"bulk-stack-{ts}-{idx:02d}"
            cidr       = cidr_blocks[idx]

            
            env = os.environ.copy()
            env["VPC_BULK_CIDR"]   = cidr
            env["VPC_BULK_NAME"]   = vpc_name
            env["VPC_BULK_STACK"]  = stack_name

            print(f"\n  [{idx+1}/{count}] Creating VPC {vpc_name} ({cidr}) …")

            cmd = [
                    self.python_exe,
                    "-m", "pytest",
                    f"{self.test_file}::test_successfully_create_a_vpc_on_aws_with_detailed_logging",
                    "-q",
                 ]


            result = subprocess.run(cmd, env=env, text=True, capture_output=True)
            if result.returncode == 0:
                print(f"  {vpc_name} created successfully\n")
            else:
                print(f"  {vpc_name} FAILED\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}\n")
            time.sleep(1)   



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python vpc_creation_wrapper.py <count> <cidr1> [<cidr2> …]")
        sys.exit(1)

    cnt = int(sys.argv[1])
    cidrs = sys.argv[2:]
    wrapper = VPCBulkWrapper()
    wrapper.create_vpcs(cnt, cidrs)
'''