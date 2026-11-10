#!/usr/bin/env python3

import unittest

from validate_state import validate


def valid_state():
    return {
        "mode": "single", "depth": "blitz", "lite": False,
        "experience": "intermediate", "tone": "straightforward",
        "focus": "performance", "audience": "mixed", "current_beat": "resolution",
        "decision_count": 3, "ended": True, "scars": [], "deferred_consequences": [],
        "judgment_signals": {"risk": "balanced", "governance": "medium", "empathy": "high",
                             "evidence": "strong", "repair": "consistent"},
    }


class StateTests(unittest.TestCase):
    def version_two(self):
        state = valid_state()
        del state['ended']
        state.update(schema_version='2.0',status='stopped',decision_count=1,campaign_phase='',
                     capabilities=['read metadata'],constraints=['no admin access'],
                     decision_history=['Investigated the metric'],
                     stakeholders=[{'name':'Morgan','incentive':'accurate metrics','trust':'uncertain'}])
        return state

    def test_explicit_early_stop_is_valid(self):
        self.assertTrue(validate(self.version_two())['valid'])

    def test_completed_minimum_and_history_required(self):
        state = self.version_two()
        state['status']='completed'
        with self.assertRaisesRegex(ValueError,'before'):
            validate(state)
        state['status']='active'
        state['decision_history']=[]
        with self.assertRaisesRegex(ValueError,'history'):
            validate(state)

    def test_campaign_resume_requires_phase(self):
        state = self.version_two()
        state['mode']='campaign'
        with self.assertRaisesRegex(ValueError,'phase'):
            validate(state)

    def test_valid_completed_blitz(self):
        self.assertTrue(validate(valid_state())["valid"])

    def test_rejects_campaign_lite(self):
        state = valid_state()
        state.update(mode="campaign", lite=True)
        with self.assertRaisesRegex(ValueError, "incompatible"):
            validate(state)

    def test_rejects_early_ending(self):
        state = valid_state()
        state["decision_count"] = 2
        with self.assertRaisesRegex(ValueError, "before"):
            validate(state)

    def test_allows_interrupted_scenario(self):
        state = valid_state()
        state.update(ended=False, decision_count=1)
        self.assertTrue(validate(state)["valid"])


if __name__ == "__main__":
    unittest.main()
