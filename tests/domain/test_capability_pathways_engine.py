from __future__ import annotations

import unittest
from capability_pathways.profiles.institution import DomainRecord
from capability_pathways.planning.dependency_graph import adjusted_effect, equity_summary, observed_gain, persistence


class BiasAdjustmentTests(unittest.TestCase):
    def record(self, key, language="a", outcome=75):
        return DomainRecord(key, {"institution_id": key, "country_group": "g5", "capability_track": "math", "staff_count": 100,
            "staff_hours": 1200, "baseline_level": 60, "target_level": outcome, "profile_missing_rate": .05,
            "mentor_capacity": .4, "compute_access": .9, "language_support": language, "participation_consent": .95})

    def test_adjustment_shrinks_observed_gain(self):
        record = self.record("a")
        self.assertGreater(observed_gain(record), adjusted_effect(record)["adjusted"])

    def test_equity_and_persistence(self):
        rows = [self.record("a", "x", 80), self.record("b", "y", 65)]
        self.assertGreater(equity_summary(rows)["gap"], 0.0)
        self.assertTrue(0.0 <= persistence(rows)["stability"] <= 1.0)
