"""Unittest for papi.util helper Methods"""
import unittest
from papi.util import parse_slurm_output, parse_sacct_output 

class TestUtil(unittest.TestCase):
    """Unittest for papi.util helper Methods"""
    def setUp(self):
        pass

    def test_parse_slurm_output(self):
        """Unit test for parse_slurm_output"""
        str_ok = 'Submitted batch job 100 on cluster mmp2'
        str_missing_id = 'Submitted batch job  on cluster mmp2'
        str_id_no_int = 'Submitted batch job false on cluster mmp2'
        str_none = 'None'
        str_empty = ''
        self.assertEqual(parse_slurm_output(str_ok), (100,'mmp2'))
        self.assertEqual(parse_slurm_output(str_missing_id), (-1,''))
        self.assertEqual(parse_slurm_output(str_id_no_int), (-1,''))
        self.assertEqual(parse_slurm_output(str_empty), (-1,''))
        self.assertEqual(parse_slurm_output(str_none), (-1,''))

    def test_parse_sacct_output(self):
        """Unit test for parse_sacct_output"""
        str_ok = """User|JobID|JobName|Partition|State|Timelimit|Start|End|Elapsed|MaxRSS|MaxVMSize|NNodes|NCPUS|NodeList
        USER|392379|ws01_sam_maize_nutr060_seedorg|mpp2_batch|COMPLETED|2-00:00:00|2020-02-13T12:00:25|2020-02-13T12:07:39|00:07:14|||1|28|mpp2r08c01s06
        USER|393250|merge_partitions|mpp2_batch|COMPLETED|01:00:00|2020-02-13T13:15:10|2020-02-13T13:15:26|00:00:16|||1|28|mpp2r03c01s05"""

        str_missing_body = """User|JobID|JobName|Partition|State|Timelimit|Start|End|Elapsed|MaxRSS|MaxVMSize|NNodes|NCPUS|NodeList"""
        str_missing_header = """USER|392379|ws01_sam_maize_nutr060_seedorg|mpp2_batch|COMPLETED|2-00:00:00|2020-02-13T12:00:25|2020-02-13T12:07:39|00:07:14|||1|28|mpp2r08c01s06"""
        str_empty = ''
        str_none = 'none'
        self.assertEqual(type(parse_sacct_output(str_ok)), type({}))
        self.assertEqual(len(parse_sacct_output(str_ok)), 2)
        self.assertEqual(parse_sacct_output(str_ok)['392379']['JobID'], '392379')
        self.assertEqual(parse_sacct_output(str_missing_body), {})
        self.assertEqual(parse_sacct_output(str_missing_header), {})
        self.assertEqual(parse_sacct_output(str_empty), {})
        self.assertEqual(parse_sacct_output(str_none), {})


if __name__ == '__main__':
    unittest.main()
