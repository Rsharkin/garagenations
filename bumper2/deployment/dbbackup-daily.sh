#!/bin/bash
 log_file="/var/log/bumper2/backup.log"
 echo "/////////////////////////////////////////////////////////////////////" >> $log_file
# Database credentials
 user="ninja"
 password="BumPer@(!!"
 host="localhost"
 db_name="bumper2"
# Other options
 backup_path="/home/ubuntu/db_backup_do_not_delete_s3_mapped"
 #date=$(date +"%d-%b-%Y")
 date="$(date +'%d_%m_%Y_%H_%M_%S')"
 echo "Starting backup on " $date >> $log_file
 full_file_name="$backup_path/$db_name-$date.sql"
 zip_file_name="$full_file_name.gz"
# Set default file permissions
# umask 177
# Dump database into SQL file
 mysqldump --user=$user --password=$password --host=$host $db_name > $full_file_name

 chmod 655 $full_file_name
 gzip $full_file_name
 echo "syncing to s3" >> $log_file
 s3cmd --config /home/ubuntu/.s3cfg sync "/home/ubuntu/db_backup_do_not_delete_s3_mapped/" "s3://unbox-bumper-dbbackup/"  >> $log_file
 
 echo "/////////////////////////////////////////////////////////////////////" >> $log_file
 echo $zip_file_name

# Delete files older than 30 days
 find $backup_path/* -mtime +7 -exec rm {} \;

