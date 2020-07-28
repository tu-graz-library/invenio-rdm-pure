""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages        [--pageStart=<page>, --pageEnd=<page>, --pageSize=<page>]
    shell_interface.py logs
    shell_interface.py delete
    shell_interface.py uuid
    shell_interface.py owner        [--identifier=<value>, --identifierValue=<value>]
    shell_interface.py group_split [--oldGroup=<recid>, --newGroups=<recid>]
    shell_interface.py group_merge [--oldGroups=<recid>, --newGroup=<recid>]
    shell_interface.py pure_import
    shell_interface.py testing

Options:
    --pageStart=<page>      Initial page [default:  1].
    --pageEnd=<page>        Ending page  [default:  2].
    --pageSize=<page>       Page size    [default: 10].
    --oldGroup=<recid>      Old group externalId.
    --newGroups=<recid>     List of new groups externalIds separated by a space.
    --oldGroups=<recid>     List of old groups externalIds separated by a space.
    --newGroup=<recid>      New group externalId.
    --identifier=<value>    Run process identifying the user with externalId or orcid
    --identifierValue=<value>    User externalId or orcid
    -h --help               Show this screen.
    --version               Show version.
"""
from docopt import docopt
from shell_interface import ShellInterface, method_call
from source.general_functions import check_if_directory_exists

if __name__ == "__main__":
    arguments = docopt(__doc__, version="Pure synchronizer 1.0")
    check_if_directory_exists("data/temporary_files")
    # Create new instance
    shell_interface = ShellInterface()

    # Calls the method given in the arguments
    method_call(shell_interface, arguments)
