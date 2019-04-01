#! /usr/bin/env python3

"""
Usage
-----
This script should be run from the root directory (one up from this script)


todo: This bit
$ cd lama_phenotype_detection
$ scripts/lama_stats.py -c <path to stats config> -w <Path to wild type diretory>
"""
from pathlib import Path

from lama.stats.permutation_stats.run_permutation_stats import run

if __name__ == '__main__':

    import argparse
    import numpy as np

    parser = argparse.ArgumentParser("Permutation-based stats")
    parser.add_argument('-w', '--wt_dir', dest='wt_dir', help='wildtype registration directory', required=True, type=Path)
    parser.add_argument('-m', '--mut_dir', dest='mut_dir', help='mutant registration directory', required=True, type=Path)
    parser.add_argument('-o', '--out_dir', dest='out_dir', help='permutation results directory', required=True, type=Path)
    parser.add_argument('-l', '--label_info', dest='label_info', help='path to label info csv file', required=False, default=None,  type=Path)
    parser.add_argument('-n', '--num_perm', dest='num_perm', help='number of permutations to do', type=np.int,
                        required=False, default=1000)

    args = parser.parse_args()

    run(args.wt_dir, args.mut_dir, args.out_dir, args.num_perm, label_info=args.label_info)