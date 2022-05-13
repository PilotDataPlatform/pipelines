# Dicom header editor

## Build docker

docker build -t indoc/dcmedit:v0.1 .

## Run docker

### a) Suppose the input file and output dir are:

FIN=/path/{Project_id}/path/fname.zip  # project ID has to be included in the path, which will be used to trim the filename to session name
ODIR=/dirA/dirB
WDIR=/dirA/tmpdir
LOGFILE=/LOGS/dcm.log # file has to exist

### b) Run docker using the command:

docker run -v $FIN:$FIN -v $DIR:$DIR -v $WDIR:$WDIR -v $LOGFILE:$LOGFILE indoc/dcmedit:edge /usr/bin/python3 scripts/dcm_edit.py -i $FIN -o $DIR -t $WORKDIR -l $LOGFILE

### c) Edited file will be: /dirA/dirB/fname_edited.zip

### See file sample_run.sh for running it as current user.
