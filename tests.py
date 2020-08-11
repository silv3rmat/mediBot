import unittest
from preferences import HourPreference, HourTarget, DateTarget, DatePreference, PreferenceParser
from datetime import datetime


class TestHourPreferences(unittest.TestCase):

    def test_target(self):
        target = HourTarget('10:00', '12:00')
        self.assertEqual(target.max_target, 12 * 60)
        self.assertEqual(target.min_target, 10 * 60)
        self.assertEqual(target.get_distance('11:00'), 0)
        self.assertEqual(target.get_distance('10:00'), 0)
        self.assertEqual(target.get_distance('12:00'), 0)
        self.assertEqual(target.get_distance('6:00'), 4 * 60)
        self.assertEqual(target.get_distance('6:30'), 3 * 60 + 30)
        self.assertEqual(target.get_distance('15:00'), 3 * 60)

    def test_preference(self):
        targets = [HourTarget('12:30', '16:30'), ]
        preference = HourPreference(100, targets)
        self.assertEqual(preference.maximum_possible_distance(), 6 * 60 + 30)
        targets = [HourTarget('6:00', '8:00'), ]
        preference = HourPreference(100, targets)
        self.assertEqual(preference.maximum_possible_distance(), (21 - 8) * 60)
        targets = [HourTarget('6:00', '8:00'), HourTarget('19:00', '21:00')]
        preference = HourPreference(100, targets)
        self.assertEqual(preference.maximum_possible_distance(), (19 - 8) / 2 * 60)

    def test_single_target(self):
        targets = [HourTarget('12:30', '16:30'), ]
        preference = HourPreference(100, targets)
        self.assertEqual(preference.get_normalized_distance({'hour': '12:30'}), 0)
        self.assertEqual(preference.get_normalized_distance({'hour': '16:30'}), 0)
        self.assertEqual(preference.get_normalized_distance({'hour': '13:00'}), 0)
        self.assertEqual(preference.get_normalized_distance({'hour': '6:00'}), 1)
        targets = [HourTarget('6:00', '9:00'), ]
        preference = HourPreference(80, targets)
        self.assertEqual(preference.get_normalized_distance({'hour': '21:00'}), 0.8)


class TestDatePreference(unittest.TestCase):

    def test_target(self):
        target = DateTarget('01-03-2020')
        self.assertEqual(target.target_value, datetime(year=2020, day=1, month=3))
        self.assertEqual(target.get_distance('02-03-2020'), 1)
        self.assertEqual(target.get_distance('28-02-2020'), 2)
        self.assertEqual(target.get_distance('01-03-2020'), 0)
        self.assertEqual(target.get_distance('02-04-2020'), 32)
        self.assertEqual(target.get_distance('01-03-2021'), 365)

    def test_single_preference(self):
        target = [DateTarget('01-03-2020'), ]
        preference = DatePreference(100, target)
        self.assertEqual(
            preference.maximum_possible_distance(
                today=datetime(year=2020, month=2, day=27),
                last_day=datetime(year=2020, month=3, day=31)),

            30
        )

    def test_single_preference_low_limit(self):
        target = [DateTarget('01-03-2020'), ]
        preference = DatePreference(100, target)
        self.assertEqual(
            preference.maximum_possible_distance(
                today=datetime(year=2020, month=3, day=1),
                last_day=datetime(year=2020, month=3, day=31)),

            30
        )

    def test_single_preference_high_limit(self):
        target = [DateTarget('31-03-2020'), ]
        preference = DatePreference(100, target)
        self.assertEqual(
            preference.maximum_possible_distance(
                today=datetime(year=2020, month=3, day=1),
                last_day=datetime(year=2020, month=3, day=31)
            ),

            30
        )

    def test_two_preferences_one_low_between(self):
        target = [DateTarget('01-03-2020'), DateTarget('20-03-2020')]
        preference = DatePreference(100, target)
        self.assertEqual(
            preference.maximum_possible_distance(
                today=datetime(year=2020, month=3, day=1),
                last_day=datetime(year=2020, month=3, day=25)
            ),

            9.5
        )

    def test_two_preferences_one_low_above(self):
        target = [DateTarget('01-03-2020'), DateTarget('10-03-2020')]
        preference = DatePreference(100, target)
        self.assertEqual(
            preference.maximum_possible_distance(
                today=datetime(year=2020, month=3, day=1),
                last_day=datetime(year=2020, month=3, day=25)
            ),

            15
        )


class TestParser(unittest.TestCase):

    def test_parser_standard(self):
        hour_preference = HourPreference(
            80,
            [
                HourTarget('06:00', '08:00'),
                HourTarget('18:00', '21:00'),
            ]
        )
        date_preference = DatePreference(
            20,
            [
                DateTarget('02-03-2020'),
                DateTarget('03-03-2020'),
            ]
        )

        parser = PreferenceParser((hour_preference, date_preference))
        self.assertEqual(parser.compile_distance({'hour': '06:00', 'date': '02-03-2020'}), 0)
        self.assertEqual(parser.compile_distance(
            {'hour': '06:00', 'date': '04-03-2020'},
            today=datetime(year=2020, day=1, month=3),
            last_day=datetime(year=2020, month=3, day=5)),
            0.1
        )

    def test_empty_parser(self):
        parser = PreferenceParser([])
        self.assertEqual(parser.compile_distance({'hour': '06:00', 'date': '02-03-2020'}), 0)
        self.assertEqual(parser.compile_distance(
            {'hour': '06:00', 'date': '04-03-2020'},
            today=datetime(year=2020, day=1, month=3),
            last_day=datetime(year=2020, month=3, day=5)),
            0
        )
