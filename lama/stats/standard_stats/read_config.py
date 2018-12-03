"""
Read the stats config and do some validation.
"""
import numbers
from pathlib import Path
from addict import Dict
import yaml
from functools import partial
# from strictyaml import load, Map, Str, Int, Seq, Optional, YAMLError


def read(config_path: Path) -> Dict:

    with open(config_path, 'r') as fh:

        config_yaml = yaml.load(fh)
        config = Dict(config_yaml)

        validate(config)
        return config


def validate(config: Dict):
    """
    Check for valid entries in the stats config

    Parameters
    ----------
    config
        The stats config

    Raises
    ------
    ValueError if the config file in invalid

    """
    def path(path):
        return True if Path(path).is_file() else False

    def seq(it, allowed):
        if hasattr(it, '__iter__'):
            given = set(it)
            if len(given) != len(given.intersection(allowed)):
                return False
            else:
                return True
        else:
            return False

    def num(n, min=None, max=None):
        if not isinstance(n, numbers.Number):
            raise ValueError(f'{key} must be a number')
        wrong = False
        if min is not None:
            if n < min:
                wrong = True
        if max is not None:
            if n > max:
                wrong = True
        if wrong:
            raise ValueError(f'{key} should be a number with min {min} and max {max}')



    schema = {
        'stats_types': {
            'required': True,
            'validate': (seq, ['intensity', 'jacobians', 'organ_volume'])
        },
        'blur_fwhm': {
            'required': False,
            'validate': (num, 0)
        },
        'voxel_size':{
            'required': False,
            'validate': (num, 0)
        },
        'mask': {
            'required': True,
            'validate': [path]
        },
        'label_info':{
            'required': False,
            'validate': [path]
        },
        'label_map':{
            'required': True,
            'validate': [path]
        },
        'reg_folder': {
            'required': False,
            'validate': [lambda x: isinstance(x, str)]
        },
        'jac_folder': {
            'required': False,
            'validate': [lambda x: isinstance(x, str)]
        }

    }

    # Check for required keys in config
    for key, data in schema.items():
        if data['required']:
            if key not in config.keys():
                raise ValueError(f'Required key {key} not present in config')

    # Validate the data in the config
    for key, data in config.items():

        if key not in schema:
            raise ValueError(f'{key} is anot a valid stats entry\nValid keys are {schema.keys()}')

        # Do validation on values
        v = schema[key]['validate']
        if len(v) == 1:
            v[0](data)
        else:
            v[0](data, v[1])