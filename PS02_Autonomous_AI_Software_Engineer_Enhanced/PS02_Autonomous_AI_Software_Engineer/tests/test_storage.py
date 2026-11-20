import os, tempfile, unittest
from app.services.storage import write_project_file, list_project_files

class StorageTests(unittest.TestCase):
    def test_write_and_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_project_file(tmp,"src/main.py","print('ok')")
            self.assertEqual(list_project_files(tmp)[0]["path"],"src/main.py")
    def test_reject_parent_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): write_project_file(tmp,"../escape.py","bad")
    def test_reject_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): write_project_file(tmp,os.path.abspath("escape.py"),"bad")

if __name__=="__main__": unittest.main()
