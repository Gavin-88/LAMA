import numpy as np
import SimpleITK as sitk
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import FloatVector
import rpy2.robjects as robj
import scipy.stats.mstats as mstats # Stats module that works on masked numpy arrays

rstats = importr('stats')


class AbstractStatisticalTest(object):
    """
    Generates the statistics. Can be all against all or each mutant against all wildtypes
    """
    def __init__(self, wt_data, mut_data):
        """
        Parameters
        ----------
        masked_wt_data: list
            list of masked 1D ndarrays
        masked_mut_data: list
            list of masked 1D ndarrays
        """
        self.masked_wt_data = wt_data
        self.masked_mut_data = mut_data
        self.filtered_tscores = False  # The final result will be stored here

    def run(self):
        raise NotImplementedError


    @staticmethod
    def _result_cutoff_filter(tstats, qvalues):
        """
        Convert to numpy arrays and set to zero any tscore that has a corresponding pvalue > 0.05

        Parameters
        ----------

        """
        assert len(tstats) == len(qvalues)
        t = np.array(tstats)
        q = np.array(qvalues)
        mask = q > 0.05  # remove hard coding
        t[mask] = 0

        return t

    def get_result_array(self):
        return self.filtered_tscores



class TTest(AbstractStatisticalTest):
    """
    Compare all the mutants against all the wild type. Generate a stats overlay
    """
    def __init__(self, *args):
        super(TTest, self).__init__(*args)
        self.stats_method_object = None
        self.fdr_class = BenjaminiHochberg

    def run(self):
        """
        Returns
        -------
        sitk image:
            the stats overlay
        """

        # The masked pvalues will be Nan
        # The masked tsatistics come out as 1.0
        tstats, pvalues = mstats.ttest_ind(self.masked_mut_data, self.masked_wt_data)

        # np.save('test_tstat', tstats)
        # np.save('pvale_test', pvalues.data)

        fdr = self.fdr_class(pvalues)
        qvalues = fdr.get_qvalues()

        # np.save('qvalues_test', qvalues)

        self.filtered_tscores = self._result_cutoff_filter(tstats, qvalues)


class AbstractFalseDiscoveryCorrection(object):
    """
    Given a set of pvalues or other statistical measure, correct based on a method defined in the subclass
    """
    def __init__(self, masked_pvalues):
        """
        Parameters
        ----------
        pvalues: array
            list of pvalues to correct
        mask: numpy 3D array
        """
        self.pvalues = masked_pvalues

    def get_qvalues(self):
        raise NotImplementedError


class BenjaminiHochberg(AbstractFalseDiscoveryCorrection):
    def __init__(self, *args):
        super(BenjaminiHochberg, self).__init__(*args)

    def get_qvalues(self):
        qvals = np.array(rstats.p_adjust(FloatVector(self.pvalues), method='BH'))
        qvals[np.isnan(qvals)] = 1
        qvals[np.isneginf(qvals)] = 1
        qvals[np.isinf(qvals)] = 1
        return qvals

class OneAgainstManytest(object):
    def __init__(self, wt_data, mut_data):
        """
        Perform a pixel-wise z-score analysis of mutants compared to a set of  wild types

        Parameters
        ----------
        
        """