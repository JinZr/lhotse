from contextlib import nullcontext as does_not_raise
from math import isclose

import pytest

from lhotse.cut import CutSet, MixedCut
from lhotse.supervision import SupervisionSegment


# Note:
# Definitions for `cut1`, `cut2` and `cut_set` parameters are standard Pytest fixtures located in test/cut/conftest.py


def test_append_cut_duration_and_supervisions(cut1, cut2):
    appended_cut = cut1.append(cut2)

    assert isinstance(appended_cut, MixedCut)
    assert appended_cut.duration == 20.0
    assert appended_cut.supervisions == [
        SupervisionSegment(id='sup-1', recording_id='irrelevant', start=0.5, duration=6.0),
        SupervisionSegment(id='sup-2', recording_id='irrelevant', start=7.0, duration=2.0),
        SupervisionSegment(id='sup-3', recording_id='irrelevant', start=13.0, duration=2.5)
    ]


@pytest.mark.parametrize(
    ['offset', 'expected_duration', 'exception_expectation'],
    [
        (0, 10.0, does_not_raise()),
        (1, 11.0, does_not_raise()),
        (5, 15.0, does_not_raise()),
        (10, 20.0, does_not_raise()),
        (100, 'irrelevant', pytest.raises(AssertionError))
    ]
)
def test_overlay_cut_duration_and_supervisions(offset, expected_duration, exception_expectation, cut1, cut2):
    with exception_expectation:
        mixed_cut = cut1.mix(cut2, offset_other_by=offset)

        assert isinstance(mixed_cut, MixedCut)
        assert mixed_cut.duration == expected_duration
        assert mixed_cut.supervisions == [
            SupervisionSegment(id='sup-1', recording_id='irrelevant', start=0.5, duration=6.0),
            SupervisionSegment(id='sup-2', recording_id='irrelevant', start=7.0, duration=2.0),
            SupervisionSegment(id='sup-3', recording_id='irrelevant', start=3.0 + offset, duration=2.5)
        ]


def test_mixed_cut_load_features():
    expected_frame_count = 1360
    cut_set = CutSet.from_yaml('test/fixtures/mix_cut_test/overlayed_cut_manifest.yml')
    mixed_cut = cut_set['mixed-cut-id']
    assert mixed_cut.num_frames == expected_frame_count
    assert isclose(mixed_cut.duration, 13.595)

    feats = mixed_cut.load_features()
    assert feats.shape[0] == expected_frame_count


@pytest.fixture
def mixed_audio_cut():
    cut_set = CutSet.from_yaml('test/fixtures/mix_cut_test/overlayed_audio_cut_manifest.yml')
    mixed_cut = cut_set['mixed-cut-id']
    assert isclose(mixed_cut.duration, 14.4)
    return mixed_cut


def test_mixed_cut_load_audio(mixed_audio_cut):
    audio = mixed_audio_cut.load_audio()
    assert audio.shape == (1, 230400)
