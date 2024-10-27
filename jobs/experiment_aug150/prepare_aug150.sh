#!/bin/bash

# Setup
base_dir="/usr/users/bhenne/projects/whisperseg"
prep_dir="$base_dir/data/inference"
stage_dir="$base_dir/data/data_setup"
source_dir="$base_dir/data/data_backup"
dest_dir="$base_dir/data/lemur_setup"
dest_name="aug150"

# create destination directories if they don't exist
mkdir -p "$base_dir/data/lemur_tar/data_${dest_name}"
mkdir -p "$base_dir/data/lemur_tar/labels_${dest_name}"

echo "[PREP] Loading python environment..."
module load anaconda3
source activate wseg

echo "[PREP] Preparing prep and stage directories..."
rm -rf $prep_dir/* $stage_dir/*
cp $source_dir/source/aug_150/* $prep_dir
mkdir -p "$prep_dir"/{pretrain,finetune}
mkdir -p "$stage_dir"/{pretrain,finetune}


echo "[PREP] Adding suffix to .wav files..."
# Add _PRED suffix to new .wav files to signify automatic labels
for file in "$prep_dir"/*.wav; do
  if [ ! -e "$file" ]; then
    echo "No .wav files found in $prep_dir"
    exit 1
  fi

  filename=$(basename "$file" .wav)

  if [[ "$filename" != *_PRED ]]; then
    newfile="$prep_dir/${filename}_PRED.wav"
    mv "$file" "$newfile"
  fi
done

echo "[PREP] Creating source tables from inference..."
python "$base_dir/util/make_raven_table.py" -p $prep_dir -o $prep_dir -e jsonr

echo "[PREP] Cleaning source tables..."
python "$base_dir/util/clean_tables.py" -p "$prep_dir"

echo "[PREP] Splitting up files into pretrain/finetune..."
cp $prep_dir/*.wav "$prep_dir/finetune"
cp $prep_dir/*.jsonr "$prep_dir/finetune"
cp $prep_dir/*.txt "$prep_dir/finetune"
mv $prep_dir/*.wav "$prep_dir/pretrain"
mv $prep_dir/*.jsonr "$prep_dir/pretrain"
mv $prep_dir/*.txt "$prep_dir/pretrain"

echo "[PREP] Creating .json annotation files..."
python "$base_dir/util/make_json.py" -p "$prep_dir/finetune" -t 0.5 -d 2.5 -o "$prep_dir/finetune"
python "$base_dir/util/make_json.py" -p "$prep_dir/pretrain" -t 0.5 -d 2.5 -o "$prep_dir/pretrain" -a animal

echo "[PREP] Removing all pretrain .wavs that have 0 annotations..."
del_count=0
for jsonr_file in "$prep_dir/pretrain"/*.jsonr; do
  base_name=$(basename "$jsonr_file" .jsonr)
  
  if [ ! -f "$prep_dir/pretrain/${base_name}_PRED.json" ]; then
    rm -f $prep_dir/pretrain/$base_name*
    ((del_count++))
  fi
done
echo "[PREP] Removed $del_count .wav files and metadata"

echo "[PREP] Removing all finetune .wavs that have 0 annotations..."
del_count=0
for jsonr_file in "$prep_dir/finetune"/*.jsonr; do
  base_name=$(basename "$jsonr_file" .jsonr)
  
  if [ ! -f "$prep_dir/finetune/${base_name}_PRED.json" ]; then
    rm -f $prep_dir/finetune/$base_name*
    ((del_count++))
  fi
done
echo "[PREP] Removed $del_count .wav files and metadata"

echo "[PREP] Trimming .wavs..."
python "$base_dir/util/trim_wavs.py" -p "$prep_dir/finetune"
python "$base_dir/util/trim_wavs.py" -p "$prep_dir/pretrain"

echo "[PREP] Preparing hand-labeled data..."
python "$base_dir/util/make_json.py" -p "$source_dir/finetune" -t 0.5 -d 2.5 -o "$source_dir/finetune" -a animal_filter_replace -f mo
python "$base_dir/util/make_json.py" -p "$source_dir/finetune" -t 0.5 -d 2.5 -o "$source_dir/pretrain" -a animal
python "$base_dir/util/trim_wavs.py" -p "$source_dir/finetune" -S
python "$base_dir/util/trim_wavs.py" -p "$source_dir/pretrain" -S

echo "[PREP] Copy prepared files to staging directory..."
# Auto-annotations
cp $prep_dir/finetune/* "$stage_dir/finetune"
cp $prep_dir/pretrain/* "$stage_dir/pretrain"
# Hand-labelled
cp $source_dir/finetune/*.json "$stage_dir/finetune"
cp $source_dir/finetune/*.wav "$stage_dir/finetune"

cp $source_dir/pretrain/*.json "$stage_dir/pretrain"
cp $source_dir/pretrain/*.wav "$stage_dir/pretrain"

files=(
    "\(2019_03_15-12_02_11\)_CSWMUW240241_0000_first*"
    "\(2019_03_15-12_02_11\)_CSWMUW240241_0001_first*"
    "\(2021_01_17-03_53_54\)_ASWMUX209084_0003_first*"
    "\(2021_04_21-19_04_26\)_ASWMUX209084_0000_first*"
    "\(2023_10_05-09_05_06\)_ASWMUX208980_0017_second*"
    "\(2023_10_10-12_07_50\)_CSWMUW240241_0001_second*"
    "\(2023_10_18-10_06_01\)_ASWMUX209146_0024_second*"
)

# Label .tars
echo "[PREP] Creating label_<x>.tar configurations..."
cfg_count=1
for test_file in "${files[@]}"; do
    # reset lemur_setup to default
    rm -f "$dest_dir"/pretrain/*
    rm -f "$dest_dir"/finetune/*
    rm -f "$dest_dir"/test/*
    cp "$stage_dir"/pretrain/*.json "$dest_dir"/pretrain/
    cp "$stage_dir"/finetune/*.json "$dest_dir"/finetune/

    # split up test file
    mv "$dest_dir"/pretrain/$test_file "$dest_dir"/test
    mv "$dest_dir"/finetune/$test_file "$dest_dir"/test

    # create tar
    cd "$dest_dir"
    tar -cf "lemur_labels_cfg${cfg_count}_${dest_name}.tar" *
    mv "$dest_dir"/lemur_labels* "$base_dir/data/lemur_tar/labels_${dest_name}"
    ((cfg_count++))
done

# Data .tars
echo "[PREP] Creating data_<x>.tar configurations..."
cfg_count=1
for test_file in "${files[@]}"; do
    # reset lemur_setup to default
    rm -f "$dest_dir"/pretrain/*
    rm -f "$dest_dir"/finetune/*
    rm -f "$dest_dir"/test/*
    cp "$stage_dir"/pretrain/*.wav "$dest_dir"/pretrain/
    cp "$stage_dir"/finetune/*.wav "$dest_dir"/finetune/

    # split up test file
    mv "$dest_dir"/pretrain/$test_file "$dest_dir"/test
    mv "$dest_dir"/finetune/$test_file "$dest_dir"/test

    # create tar
    cd "$dest_dir"
    tar -cf "lemur_data_cfg${cfg_count}_${dest_name}.tar" *
    mv "$dest_dir"/lemur_data* "$base_dir/data/lemur_tar/data_${dest_name}"
    ((cfg_count++))
done