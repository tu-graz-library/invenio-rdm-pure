from source.rdm.delete_record       import Delete
from source.reports                 import Reports
from setup                          import data_files_name

def rdm_duplicate_records():

    report = Reports()
    delete = Delete()

    # Reads file containing all RDM records
    all_records = open(data_files_name['all_rdm_records'], 'r').readlines()                       

    temp_arr = []
    count_deleted = 0

    # Starts iterating from the last uploaded records
    for record in reversed(all_records):

        record_split = record.split(' ')
        
        uuid = record_split[0]
        recid = record_split[1].strip('\n')

        # Checks if they are duplicates
        if uuid in temp_arr:
            count_deleted += 1
            delete.record(recid)
            continue
        temp_arr.append(uuid)

    if count_deleted == 0:
        report.add('\nThere are no duplicate records to delete\n')

    report.add(f'Total items: {len(all_records)}\nDeleted: {count_deleted}\n')

        
        

