echo "Welcome to configuration's copy script"

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

check_integrity() {
    echo "checking integrety "
    cd $CUR_DIR
    gsha256sum -c configurations_copy_test.py.sha256
    if [ $? -ne 0 ]; then
        echo "The script configurations_copy_test.py has been modified. Aborting."
        exit 1
    fi
}

check_integrity

source $CUR_DIR/config_file

echo "organisation name :(eg: AJIO) (this will appear in the replica's name) : $ORG_NAME"
echo "Source idx name: $SRC_IDX_NAME"
echo "Target index name: $TGT_IDX_NAME"
echo "Source index API key: $SRC_IDX_API_KEY"
echo "Source index API key secret: $SRC_IDX_API_SECRET"
echo "Target index API key: $TGT_IDX_API_KEY"
echo "Target index API key secret: $TGT_IDX_API_SECRET"

while true; do
    read -p "Please check the above properties and confirm to proceed? (Y/N): " proceed
    case $proceed in
        [Yy]* )
            echo "executing $CUR_DIR/configurations_copy_test.py"
            python3 "$CUR_DIR/configurations_copy_test.py"
            break ;;
        [Nn]* )
            echo "exiting the script"
            break ;;
        * )
            echo "Please enter Y or N" ;;
    esac
done

