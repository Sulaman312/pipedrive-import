import logging
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "importer"))
import importer


class FakeMetadataClient(importer.PipedriveClient):
    def __init__(self):
        super().__init__("token", "https://example.invalid/v1", logging.getLogger("test"))

    def request(self, method, path, **kwargs):
        responses = {
            "dealFields": [],
            "organizationFields": [],
            "personFields": [],
            "pipelines": [{"id": 10, "name": "CAMILLE - PME-KMU"}, {"id": 20, "name": "Other"}],
            "stages": [
                {"id": 101, "name": "Prospects", "pipeline_id": 10, "order_nr": 1},
                {"id": 201, "name": "Prospects", "pipeline_id": 20, "order_nr": 1},
            ],
            "users": [],
        }
        return responses[path]


class ImporterTests(unittest.TestCase):
    def test_metadata_restricts_stages_to_target_pipeline(self):
        with patch.dict(os.environ, {"PIPEDRIVE_PIPELINE_NAME": "CAMILLE - PME-KMU"}):
            metadata = FakeMetadataClient().load_metadata()
        self.assertEqual(metadata.target_pipeline_id, 10)
        self.assertEqual(metadata.stages, {"prospects": 101})
        self.assertEqual(metadata.default_stage_id, 101)

    def test_deal_search_is_limited_and_locally_exact(self):
        client = FakeMetadataClient()
        long_title = "A" * 120
        captured = {}

        def request(method, path, **kwargs):
            captured.update(kwargs["params"])
            return {"items": [{"item": {"id": 8, "title": long_title, "organization": {"id": 1}}}]}

        client.request = request
        result = client.search_deal(long_title, 1, None)
        self.assertEqual(result["id"], 8)
        self.assertEqual(len(captured["term"]), 100)
        self.assertEqual(captured["exact_match"], 0)
        self.assertNotIn("status", captured)

    def test_person_search_is_limited_and_locally_exact(self):
        client = FakeMetadataClient()
        long_name = "Long person name " * 10
        captured = {}

        def request(method, path, **kwargs):
            captured.update(kwargs["params"])
            return {"items": [{"item": {"id": 9, "name": long_name}}]}

        client.request = request
        result = client.search_person_by_name(long_name)
        self.assertEqual(result["id"], 9)
        self.assertEqual(len(captured["term"]), 100)
        self.assertEqual(captured["exact_match"], 0)

    def test_missing_pipeline_fails_before_import(self):
        with patch.dict(os.environ, {"PIPEDRIVE_PIPELINE_NAME": "Missing"}):
            with self.assertRaisesRegex(importer.ImporterError, "pipeline not found"):
                FakeMetadataClient().load_metadata()

    def test_invalid_email_is_skipped(self):
        metadata = importer.PipedriveMetadata(
            field_lookup={}, field_options={}, stages={}, users={},
            target_pipeline_id=10, default_stage_id=101,
            target_pipeline_name="CAMILLE - PME-KMU",
        )
        stats = importer.ImportStats()
        value = importer.resolve_pipedrive_value(
            "person", "email", "Adresse e-mail (Travail)",
            "this is a product description", metadata, stats, logging.getLogger("test"),
        )
        self.assertIsNone(value)
        self.assertIn("person: invalid Adresse e-mail (Travail) value", stats.skipped_fields)

    def test_existing_deal_is_skipped(self):
        class DealClient:
            def search_deal(self, title, org_id, person_id):
                return {"id": 55, "title": title}

            def create_entity(self, entity, payload):
                raise AssertionError("existing deal must not be created")

        deal_id, action = importer.create_deal(
            DealClient(), {"title": "Example"}, 1, 2, False, logging.getLogger("test")
        )
        self.assertEqual((deal_id, action), (55, "skipped"))

    def test_process_row_forces_pipeline_and_default_stage(self):
        metadata = importer.PipedriveMetadata(
            field_lookup={"deal": {}, "organization": {}, "person": {}},
            field_options={"deal": {}, "organization": {}, "person": {}},
            stages={"prospects": 101},
            users={},
            target_pipeline_id=10,
            default_stage_id=101,
            target_pipeline_name="CAMILLE - PME-KMU",
        )
        stats = importer.ImportStats(rows=1)
        row = pd.Series({"Affaire - Titre de l'affaire - CD": "Example"})

        class Client:
            def search_organization_by_name(self, name): return None
            def search_person_by_name(self, name): return None
            def search_person_by_email(self, email): return None
            def search_deal(self, title, org_id, person_id): return None
            def create_entity(self, entity, payload):
                if entity == "deal":
                    self.deal_payload = payload
                    return {"id": 99}
                return {"id": 1}
            def update_entity(self, entity, entity_id, payload): return {"id": entity_id}

        client = Client()
        importer.process_row(2, row, client, metadata.field_lookup, metadata, stats, False, logging.getLogger("test"))
        self.assertEqual(client.deal_payload["pipeline_id"], 10)
        self.assertEqual(client.deal_payload["stage_id"], 101)
        self.assertEqual(stats.created_deal_ids, [99])


if __name__ == "__main__":
    unittest.main()
