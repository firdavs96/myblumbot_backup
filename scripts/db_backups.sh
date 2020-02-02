TIME=$(date +%b-%d-%y)
export $(grep -v '^#' /root/myblumbot/.env | xargs)
FILENAME=backup-$TIME.tar.gz
SRCDIR=$ROOT_DIR/BlumUz.db
DESDIR=$ROOT_DIR/db_backups
tar -cpzf "$DESDIR"/"$FILENAME" "$SRCDIR"