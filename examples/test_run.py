from river.drift.adwin import ADWIN
from river.tree.hoeffding_tree_classifier import HoeffdingTreeClassifier

from fall.adaptive_learning.base import BaseBufferedAdaptiveLearner
from fall.adaptive_learning.reidentification_schedulers import DriftDetectionCheck
from fall.concept_representations import FingerprintRepresentation
from fall.data.datastream import ConceptSegmentDataStream, make_stream_concepts
from fall.data.synthetic.wind_sim import WindSimGenerator
from fall.data.transition_patterns import circular_transition_pattern
from fall.data.utils import Concept
from fall.metafeature_weighting.weighting_functions import (  # random_weighting,
    fisher_overall_weighting,
)
from fall.repository import CosineComparer

seed = 42
s0 = WindSimGenerator(concept=3, sample_random_state_init=seed)
s1 = WindSimGenerator(concept=2, sample_random_state_init=seed)
s2 = WindSimGenerator(concept=1, sample_random_state_init=seed)
s3 = WindSimGenerator(concept=0, sample_random_state_init=seed)
c0 = Concept(s0, "0")
c1 = Concept(s1, "1")
c2 = Concept(s2, "2")
c3 = Concept(s3, "3")

n_repeats = 30
pattern = circular_transition_pattern(4, n_repeats, 1.0, 1, 0.0, shuffle_order=False)

segment_length = 1000
concept_segments = make_stream_concepts([c0, c1, c2, c3], pattern, segment_length)

datastream = ConceptSegmentDataStream(concept_segments, 0, seed)

classifier = BaseBufferedAdaptiveLearner(
    classifier_constructor=lambda: HoeffdingTreeClassifier(grace_period=50),
    # representation_constructor=ErrorRateRepresentation,
    representation_constructor=FingerprintRepresentation,
    train_representation=True,
    # representation_comparer=AbsoluteValueComparer(),
    representation_comparer=CosineComparer(fisher_overall_weighting),
    drift_detector_constructor=lambda: ADWIN(delta=0.0002),
    representation_window_size=50,
    representation_update_period=1,
    reidentification_check_schedulers=[DriftDetectionCheck(100)],
    background_state_mode=None,
    drift_detection_mode="lower",
)

baseline = HoeffdingTreeClassifier()

if __name__ == "__main__":
    print(pattern)
    print(concept_segments)
    print(datastream)
    stream_iter = iter(datastream)
    for i in range(100):
        X, y = next(stream_iter)
        if X is not None:
            p = classifier.predict_one(X)
            classifier.learn_one(X, y)
