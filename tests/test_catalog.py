import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_catalog import InvalidCatalog, validate, validate_file, unique_object_pairs

BASE = Path(__file__).resolve().parents[1]


class CatalogContractTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((BASE / "catalog" / "rafgittools.v1.json").read_text())

    def test_baseline(self):
        self.assertEqual(validate_file(BASE / "catalog" / "rafgittools.v1.json"), 2)

    def test_claim_inflation_blocked(self):
        self.data["features"][0]["claim_allowed"] = True
        with self.assertRaises(InvalidCatalog):
            validate(self.data)

    def test_private_repo_blocked(self):
        self.data["features"][0]["producer_repo"] = "rafaelmeloreisnovo/private-repo"
        with self.assertRaises(InvalidCatalog):
            validate(self.data)

    def test_secret_and_email_blocked(self):
        self.data["features"][0]["description"] = "github_pat_" + "x" * 24
        with self.assertRaises(InvalidCatalog):
            validate(self.data)
        self.data["features"][0]["description"] = "Contact person@example.org now"
        with self.assertRaises(InvalidCatalog):
            validate(self.data)

    def test_duplicate_features_blocked(self):
        self.data["features"].append(dict(self.data["features"][0]))
        with self.assertRaises(InvalidCatalog):
            validate(self.data)

    def test_duplicate_json_keys_blocked(self):
        with self.assertRaises(InvalidCatalog):
            json.loads('{"x":1,"x":2}', object_pairs_hook=unique_object_pairs)


if __name__ == "__main__":
    unittest.main()
