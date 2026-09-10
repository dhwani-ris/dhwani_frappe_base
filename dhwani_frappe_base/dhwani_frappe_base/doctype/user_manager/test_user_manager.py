# Copyright (c) 2026, Dhwani RIS and Contributors
# See license.txt

from types import SimpleNamespace

import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase

from dhwani_frappe_base.dhwani_frappe_base.doctype.user_manager.user_manager import UserManager

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


def _row(program, project):
	return SimpleNamespace(program=program, project=project)


class UnitTestUserManager(UnitTestCase):
	"""
	Unit tests for UserManager.
	Use this class for testing individual functions and methods.
	"""

	def setUp(self):
		self.user_manager = UserManager.__new__(UserManager)

	def test_allows_same_project_value_across_different_programs(self):
		"""Same record name under different Program (doctype) should not be flagged."""
		program_access_table = [
			_row("District", "Mandla"),
			_row("Block", "Mandla"),
		]
		# Should not raise
		self.user_manager._validate_program_access_duplicates(program_access_table)

	def test_blocks_exact_duplicate_program_and_project_pair(self):
		"""Same (program, project) pair repeated should be blocked."""
		program_access_table = [
			_row("District", "Mandla"),
			_row("District", "Mandla"),
		]
		with self.assertRaises(frappe.ValidationError):
			self.user_manager._validate_program_access_duplicates(program_access_table)

	def test_ignores_rows_without_project(self):
		"""Rows with no project value should be skipped, not counted as duplicates."""
		program_access_table = [
			_row("District", None),
			_row("Block", None),
		]
		# Should not raise
		self.user_manager._validate_program_access_duplicates(program_access_table)

	def test_allows_distinct_program_project_pairs(self):
		program_access_table = [
			_row("District", "Mandla"),
			_row("District", "Jabalpur"),
			_row("Block", "Mandla"),
		]
		# Should not raise
		self.user_manager._validate_program_access_duplicates(program_access_table)


class IntegrationTestUserManager(IntegrationTestCase):
	"""
	Integration tests for UserManager.
	Use this class for testing interactions between multiple components.
	"""

	pass
