"""Source boundaries and missingness must survive the complementary adapter."""
import pandas as pd
import pytest
from src.data.complementary import observed_wellness_long


def test_source_scales_keys_and_missing_calendar_cells_are_preserved():
    source = pd.DataFrame({'Fatigue Data':['01.01.2020','02.01.2020','03.01.2020'],
                           'TeamA-example':[5,None,1]})
    result = observed_wellness_long({'subjective/wellness/fatigue.csv':source})
    assert result.source_value.tolist() == [5,1]
    assert result.source_date.dt.day.tolist() == [1,3]
    assert result.participant_key.eq('soccermon::TeamA-example').all()
    assert result.dataset_id.eq('soccermon_subjective').all()
    assert not any(c in result for c in ['injury','Athlete ID'])


def test_duplicate_source_wellness_keys_are_exposed():
    source = pd.DataFrame({'Date':['01.01.2020','01.01.2020'],'TeamA-example':[3,4]})
    with pytest.raises(ValueError,match='Duplicate'):
        observed_wellness_long({'subjective/wellness/fatigue.csv':source})
