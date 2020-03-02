from pysradb import SRAdb
import os
#db = SRAdb('SRAmetadb.sqlite')

def test_list_tables(sradb_connection):
    fields = sradb_connection.list_fields("sqlite_sequence")
    print(fields)
  
def test_changed_paths2():    
    wrong_filename = "SRAme'tadb2.sql.ite"
    path = os.path.join(os.getcwd(), "data", "{}".format(wrong_filename))
    try:
        db = SRAdb(path)
    except:
        pass
    assert os.path.isfile(path) == False
    #assert os.path.isfile(path) == False



test_changed_paths2()