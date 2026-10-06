"""Automated Unit & Regression Test Suite Generator.

Analyzes Python functions, data transformation logic, and pipeline scripts,
synthesizing comprehensive, production-grade pytest suites with:
- Mock/fixture data generation
- Adversarial edge cases (empty dataframes, NaN, divide-by-zero, boundary dates)
- Schema invariants and regression assertions
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class TestSuiteGeneratorEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def generate_test_suite(self, code_snippet: str) -> str:
        """Synthesizes a production pytest test suite for the provided code."""
        clean = code_snippet.strip()
        if not clean:
            return (
                "🧪 **Automated Unit & Regression Test Suite Generator**\n\n"
                "Paste your Python function, data processing logic, or report calculation:\n"
                "Usage: `/gen_tests <python function or class snippet>`\n\n"
                "Generates:\n"
                "• 📋 **Mock Fixtures**: Clean synthetic DataFrames or records\n"
                "• ⚠️ **Adversarial Edge Cases**: Empty sets, NaNs, divide-by-zero, month-end boundary dates\n"
                "• 🛡️ **Regression Invariants**: Column schema checks, non-null guarantees, precision tolerances\n"
                "• 🚀 **100% Executable**: Directly runnable with `pytest`"
            )

        system_prompt = (
            "You are a Staff Quality & Infrastructure Engineer specializing in Python data systems and AI pipelines.\n"
            "Generate a comprehensive, battle-hardened pytest test suite for the submitted code snippet.\n"
            "Structure your output as follows:\n\n"
            "### 1. 🧪 COMPLETE RUNNABLE PYTEST SUITE\n"
            "(Provide clean, self-contained Python code with pytest fixtures, parameterization, and clear test names)\n\n"
            "### 2. ⚠️ ADVERSARIAL EDGE CASES TESTED\n"
            "• Empty input / 0-row datasets\n"
            "• Null / NaN values in numerical and string fields\n"
            "• Divide-by-zero in metric or percentage computations\n"
            "• Timestamp boundaries (midnight, leap years, timezone drift)\n\n"
            "### 3. 🛡️ REGRESSION INVARIANTS PROTECTED\n"
            "(Explain the exact business rules and schema contracts enforced by these tests)\n\n"
            "### 4. 💡 EXECUTION COMMAND\n"
            "`pytest test_pipeline.py -v --tb=short`"
        )

        prompt = f"Generate an airtight pytest unit & regression test suite for this code:\n\n{clean}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return (
            "🧪 **Generated Production Pytest Test Suite**\n\n"
            f"{response.content}"
        )
