#!/usr/bin/env python


import yaml
from os.path import relpath, join, dirname
import sys
import os
import SimpleITK as sitk
import numpy as np

from _phenotype_statistics import DeformationStats, GlcmStats, IntensityStats
from _stats import TTest

# Hack. Relative package imports won't work if this module is run as __main__
sys.path.insert(0, join(os.path.dirname(__file__), '..'))
import common



STATS_METHODS = {
    'ttest': TTest
}


class LamaStats(object):
    """
    Takes a stats.yaml config file and creates appropriate PhenotypeStatitics subclasses based on which analysis is to
    be performed
    """
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.get_config()
        self.config_dir = dirname(self.config_path)
        self.stats_objects = []
        self.mask_path = self.make_path(self.config['fixed_mask'])

    def make_path(self, path):
        """
        All paths are relative to the config file dir.
        Return relative paths to the config dir
        """
        return join(self.config_dir, path)

    def get_config(self):
        with open(self.config_path) as fh:
            config = yaml.load(fh)
        return config

    def run_stats_from_config(self):
        """
        Build the regquired stats classes for each data type
        """

        fixed_mask = self.make_path(self.config.get('fixed_mask'))
        if self.config.get('inverted_tform_config'):
            inverted_tform_config = self.make_path(self.config.get('inverted_tform_config'))
            inverted_stats_dir = join(self.config_dir, 'inverted_stats')
            common.mkdir_if_not_exists(inverted_stats_dir)

        # loop over the types of data and do the required stats analysis
        mask_array = common.img_path_to_array(fixed_mask)
        for name, analysis_config in self.config['data'].iteritems():
            stats_tests = analysis_config['tests']
            mut_data_dir = self.make_path(analysis_config['mut'])
            wt_data_dir = self.make_path(analysis_config['wt'])
            outdir = join(self.config_dir, name)

            if name == 'registered_normalised':
                int_stats = IntensityStats(self.config_dir, outdir, wt_data_dir, mut_data_dir, mask_array)
                for test in stats_tests:
                    int_stats.run(STATS_METHODS[test], name)

            if name == 'jacobians':  # Jacobians and intensity use exactly the same analysis
                jac_stats = IntensityStats(self.config_dir, outdir, wt_data_dir, mut_data_dir, mask_array)
                for test in stats_tests:
                    jac_stats.run(STATS_METHODS[test], name)

            if name == 'deformations':  # Jacobians and intensity use exactly the same analysis
                def_stats = DeformationStats(self.config_dir, outdir, wt_data_dir, mut_data_dir, mask_array)
                for test in stats_tests:
                    def_stats.run(STATS_METHODS[test], name)

            if name == 'glcm':
                jac_stats = GlcmStats(self.config_dir, outdir, wt_data_dir, mut_data_dir, None)
                for test in stats_tests:
                    jac_stats.run(STATS_METHODS[test], name)


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser("Stats component of the phenotype detection pipeline")
    parser.add_argument('-c', '--config', dest='config', help='yaml config file contanign stats info', required=True)
    args = parser.parse_args()
    l = LamaStats(args.config)
    l.run_stats_from_config()