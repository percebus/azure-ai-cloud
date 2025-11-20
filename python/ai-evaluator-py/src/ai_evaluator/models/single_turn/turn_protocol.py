from ai_evaluator.models.single_turn.ground_truth_entry_protocol import GroundTruthEntryProtocol


class TurnProtocol(GroundTruthEntryProtocol):
    response: str
