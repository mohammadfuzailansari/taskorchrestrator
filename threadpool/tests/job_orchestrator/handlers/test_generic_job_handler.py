import os
import sys
import unittest



# Calculate the absolute path to the directory containing 'src'
base_threadpool = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, base_threadpool)  # Insert at the beginning to prioritize
base_src = os.path.join(base_threadpool, 'src')
sys.path.insert(1, base_src)  # Insert at the beginning to prioritize


from src.job_orchestrator.handlers.generic_job_handler import GenericJobHandler

class TestGenericJobHandler(unittest.TestCase):

  
    def test_execute_parallel_tasks(self):
        """
        Test if parallel tasks are executed properly using ThreadPoolExecutor.
        """           

        tasks = [
            {"name": "jobs.job1.task1"},
            {"name": "jobs.job1.task2", "dependencies": ["jobs.job1.task1"] }
        ]
        
        handler = GenericJobHandler(max_workers=2)
        
        # Act
        handler.execute_tasks(tasks)
        
        print(handler.results)
               
        # Check that results are correctly stored in the handler
        self.assertEqual(handler.results["jobs.job1.task1"], "From Task1")
        self.assertEqual(handler.results["jobs.job1.task2"], "From Task2 with {'jobs.job1.task1': 'From Task1'}")


    
    

if __name__ == '__main__':
    unittest.main()
