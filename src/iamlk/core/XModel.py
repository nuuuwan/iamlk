from functools import cached_property

from gig import Ent, EntType, GIGTable
from utils import Log

from iamlk.core.Joint import Joint

log = Log('XModel')

ENT_TYPE = EntType.GND
K_MAP = {
    # population-ethnicity
    'sl_tamil': 'tamil',
    'ind_tamil': 'tamil',
    'sl_moor': 'muslim',
    'malay': 'muslim',
    'burgher': 'other',
    'sl_chetty': 'other',
    'other_eth': 'other',
    'sl_chetty': 'other',
    'bharatha': 'other',
    # population-religion
    'other_christian': 'christian',
    'roman_catholic': 'christian',
}

NON_OTHER_KEYS = [
    'other',
    #
    'sinhalese',
    'tamil',
    'muslim',
    #
    'buddhist',
    'hindu',
    'christian',
    'islam',
    #
    'SLPP',
    'NDF',
    'NMPP',
    'NPP',
]

INVALID_KEYS = ['valid', 'electors', 'polled', 'rejected']
MAX_KEYS = 5


class XModel:
    def __init__(self, x_gt_list: list[GIGTable], y_gt_list: list[GIGTable]):
        self.x_gt_list = x_gt_list
        self.y_gt_list = y_gt_list
        self.weights = None

    @staticmethod
    def remap(d):
        d_new = {}
        for k, v in d.items():
            if k in INVALID_KEYS:
                continue
            k_new = K_MAP.get(k, k)
            if k_new not in NON_OTHER_KEYS:
                k_new = 'other'

            if k_new not in d_new:
                d_new[k_new] = 0
            d_new[k_new] += v
        return d_new

    @cached_property
    def keys(self):
        country = Ent.from_id('LK')

        def get_z_keys_list(z_gt_list: list[GIGTable]):
            z_keys_list = []
            for z_gt in z_gt_list:
                gt_row = country.gig(z_gt)
                d = XModel.remap(gt_row.dict)
                total = sum(d.values())
                log.debug(f'{total=}')
                z_keys_list.append(list(d.keys()))
            return z_keys_list

        return get_z_keys_list(self.x_gt_list), get_z_keys_list(
            self.y_gt_list
        )

    @cached_property
    def data(self):
        x_keys_list, y_keys_list = self.keys

        gnd_list = Ent.list_from_type(ENT_TYPE)
        x_list, y_list, w_list = [], [], []
        for i_gnd, gnd in enumerate(gnd_list):
            population = gnd.population

            def get_z(
                z_gt_list: list[GIGTable], z_keys_list: list[list[str]]
            ):
                z = []
                for z_gt, z_keys in zip(z_gt_list, z_keys_list):
                    d = XModel.remap(gnd.gig(z_gt).dict)
                    total = sum(d.values())
                    for key in z_keys:
                        z.append(d.get(key, None) / total)
                return z

            try:
                x = get_z(self.x_gt_list, x_keys_list)
                y = get_z(self.y_gt_list, y_keys_list)

                x_list.append(x)
                y_list.append(y)
                w_list.append(population)
            except BaseException:
                pass

        n = len(x_list)
        assert n == len(y_list)
        log.info(f'{n=}')
        mx = len(x_list[0])
        my = len(y_list[0])
        log.info(f'{mx=} -> {my=}')
        print(x_list[0], y_list[0], w_list[0])
        return x_list, y_list, w_list

    @cached_property
    def joint(self):
        x_list, y_list, w_list = self.data
        j = Joint(x_list, y_list, w_list)
        return j.joint


RELIGION_TO_ETHNICITY = XModel(
    [
        GIGTable('population-religion', 'regions', '2012'),
    ],
    # [
    #     GIGTable('government-elections-presidential', 'regions-ec', '2019'),
    # ],
    [
        GIGTable('population-ethnicity', 'regions', '2012'),
    ],
)

if __name__ == '__main__':
    print(RELIGION_TO_ETHNICITY.keys)
    Joint.pretty_print(RELIGION_TO_ETHNICITY.joint)
