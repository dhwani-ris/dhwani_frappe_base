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

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.role_profile_name = "Test UM Role Profile"
		if not frappe.db.exists("Role Profile", cls.role_profile_name):
			frappe.get_doc(
				{
					"doctype": "Role Profile",
					"role_profile": cls.role_profile_name,
					"roles": [{"role": "System Manager"}],
				}
			).insert(ignore_permissions=True)

	def test_program_access_is_not_mandatory(self):
		"""User Manager should save without any Program Access / User Permission rows."""
		email = "test_program_access_optional@example.com"
		for doctype in ("User Manager", "User"):
			if frappe.db.exists(doctype, email):
				frappe.delete_doc(doctype, email, force=True, ignore_permissions=True)

		doc = frappe.get_doc(
			{
				"doctype": "User Manager",
				"email": email,
				"full_name": "Test Program Access Optional",
				"role_profiles": [{"role_profile": self.role_profile_name}],
			}
		)
		# Should not raise, even with an empty Program Access table
		doc.insert(ignore_permissions=True)

		self.assertEqual(doc.get("table_fkmn"), [])
