from datetime import datetime, date, timedelta


class DoctorTarget:
    def __init__(self, target_value):
        self.target_value = target_value

    def get_distance(self, challenger):
        if self.target_value == challenger:
            return 0
        else:
            return 1


def hour_to_int(hour):
    hours, minutes = hour.split(':')
    return int(hours) * 60 + int(minutes)


class HourTarget:
    def __init__(self, min_target, max_target):
        self.min_target = hour_to_int(min_target)
        self.max_target = hour_to_int(max_target)

    def get_distance(self, challenger):
        challenger = hour_to_int(challenger)
        if self.min_target <= challenger <= self.max_target:
            return 0
        elif self.min_target > challenger:
            return self.min_target - challenger
        elif self.max_target < challenger:
            return challenger - self.max_target


class DateTarget:
    def __init__(self, target_value):
        if isinstance(target_value, datetime):
            self.target_value= target_value
        else:
            self.target_value = datetime.strptime(target_value, '%d-%m-%Y')

    def get_distance(self, challenger):
        challenger = datetime.strptime(challenger, '%d-%m-%Y')
        if challenger == self.target_value:
            return 0
        else:
            return abs((self.target_value - challenger).days)


class Preference:
    def __init__(self, dimension, weight, targets, required=False):
        self.dimension = dimension
        self.weight = weight
        self.targets = targets
        self.required = required

    def min_distance(self, challenger):
        return min([target.get_distance(challenger[self.dimension]) for target in self.targets])

    def maximum_possible_distance(self, **kwargs):
        raise NotImplementedError

    def get_normalized_distance(self, challenger, **kwargs):
        if self.required and self.min_distance(challenger)>0:
            return 10000
        else:
            return self.min_distance(challenger) / self.maximum_possible_distance(**kwargs) * self.weight / 100


class HourPreference(Preference):

    def __init__(self, weight, targets, required=False):
        super().__init__('hour', weight, targets, required)

    def maximum_possible_distance(self, **kwargs):
        minimum_avail = 6 * 60
        maximum_avail = 21 * 60
        partitions = sorted([[target.min_target, target.max_target] for target in self.targets], key=lambda x: x[0])
        distances = []
        for index, item in enumerate(partitions):
            if index == 0:
                distances.append(item[0] - minimum_avail)
                if index == len(partitions) - 1:
                    distances.append(maximum_avail - item[1])
            elif index == len(partitions) - 1:
                distances.append(maximum_avail - item[1])
                distances.append((item[0]-partitions[index-1][1]) / 2)
            else:
                distances.append((partitions[index + 1][0] - item[0]) / 2)
        return max(distances) if max(distances) > 0 else 0


class DatePreference(Preference):

    def __init__(self, weight, targets, required=False):
        super().__init__('date', weight, targets, required)

    def maximum_possible_distance(self, **kwargs):
        if 'today' not in kwargs:
            today = datetime.today()
        else:
            today = kwargs['today']

        if 'last_day' not in kwargs:
            last_day = datetime.today() + timedelta(days=40)
        else:
            last_day =kwargs['last_day']

        target_dates = sorted([target.target_value for target in self.targets])
        distances = []
        for index, item in enumerate(target_dates):
            if index == 0:
                distances.append((item - today).days-1)
                if index == len(target_dates) - 1:
                    distances.append((last_day - item).days-1)
            elif index == len(target_dates) - 1:
                distances.append((last_day - item).days-1)
                distances.append(((item-target_dates[index-1]).days-1) / 2)
            else:
                distances.append(((target_dates[index + 1] - item).days-1) / 2)
        return max(distances) if max(distances) > 0 else 0


class DoctorPreference(Preference):

    def __init__(self, weight, targets, required=False):
        super().__init__('doctor', weight, targets, required)

    def maximum_possible_distance(self, **kwargs):
        return 1


class PreferenceParser:
    def __init__(self, preferences, last_day=datetime.today()+timedelta(days=40)):
        self.preferences = preferences
        self.last_day = last_day

    def compile_distance(self, challenger, **kwargs):
        return sum([preference.get_normalized_distance(challenger, **kwargs) for preference in self.preferences])




