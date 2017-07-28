#!/bin/bash
#
# Backup current sqlite db to another folder.
#
# Example:
# ./backup.sh ~/backups rankings/db.sqlite3

# Location of this script file
SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )

# Default command-line arguments
BACKUP_FOLDER=${1:-~/backups}
DB_FILE=${2:-$SCRIPTPATH/../rankings/db.sqlite3}

# Generate filename-friendly date and time string
DATE_STR=`date -Ins | tr : -`

cp $DB_FILE $BACKUP_FOLDER/`basename $DB_FILE`.$DATE_STR