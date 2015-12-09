
import sqlite3
import json
import sys

# TODO THIS IS A MESS FIGURE OUT WHY THE ABSTRACT IS MISSING FROM SOME STUDIES!
db_location1 = "/tier2/deweylab/mnbernstein/sra_metadb/SRAmetadb.sqlite"
db_location2 = "/tier2/deweylab/mnbernstein/sra_metadb/sra_metadata.db"

def main():
    study_acc = sys.argv[1] # Argument is the study accession
    
    meta = {}
    with sqlite3.connect(db_location1) as db_conn:
        
        # title and abstract
        db_cursor = db_conn.cursor()
        sql_cmd = "SELECT study_title, study_abstract " \
            "FROM study WHERE study_accession = '%s'" % study_acc
        r = [x for x in db_cursor.execute(sql_cmd)]
        meta["title"] = r[0][0].encode('utf-8')
        meta["abstract"] = r[0][1].encode('utf-8')
        meta["time_units"] = "TODO"
        
    with sqlite3.connect(db_location2) as db_conn:

        # all experiments in the study
        sql_cmd = "SELECT experiment_accession FROM " \
            "experiment WHERE study_accession = '%s'" % study_acc
        exps = []
        e = []
        for r in db_cursor.execute(sql_cmd):
            e.append(r[0].encode('utf-8'))
            exps.append({"accession":r[0].encode('utf-8'), "time_point":"TODO", "biological_replicate":"TODO"})
        meta["experiments"] = exps
    
        with open("./%s.raw.json" % study_acc, "w") as f:
            f.write(json.dumps(meta, indent=4, separators=(',', ': ')))
    
        with open("./%s.csl" % study_acc, "w") as f:
            f.write(",".join(e))

if __name__ == "__main__":
    main()
