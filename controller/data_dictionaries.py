from typing import Literal


class DataConverter:

    def __init__(self):
        self.__gender_dict: dict[Literal['мужской', 'жунский'], Literal['m', 'f']] = {
            'мужской': 'm',
            'жунский': 'f'
        }

        self.__hand_dict: dict[Literal['левая', 'правая'], Literal['l', 'r']] = {
            'левая': 'l',
            'правая': 'r'
        }


    def convert_gender(self, gender: Literal['мужской', 'жунский']) -> Literal['m', 'f']:
        return self.__gender_dict[gender]


    def convert_hand(self, hand: Literal['левая', 'правая']) -> Literal['l', 'r']:
        return self.__hand_dict[hand]