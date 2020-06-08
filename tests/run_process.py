import os
command = '/home/bootcamp/.local/share/virtualenvs/pure_sync_rdm-fOqjLk38/bin/python /home/bootcamp/src/pure_sync_rdm/invenio_pure_sync/cli.py '

# os.system(command + 'pages  --pageStart=1 --pageEnd=2 --pageSize=1')
# os.system(command + 'pages  --pageStart=7 --pageEnd=8 --pageSize=2')
# os.system(command + "group_split --oldGroup=2267 --newGroups='13866 19428'")
# os.system(command + "group_merge --oldGroups='13866 19428' --newGroup=2267")
# os.system(command + 'logs')
# os.system(command + 'owners_list')
os.system(command + "owner --identifier='externalId'")
# os.system(command + 'changes')
# os.system(command + 'pure_import')

# os.system(command + 'delete')
# os.system(command + 'uuid')
# os.system(command + 'duplicates')
# os.system(command + 'owner_orcid')

