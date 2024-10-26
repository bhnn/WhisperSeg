#!/bin/bash

module load anaconda3
source activate wseg

base_dir="/usr/users/bhenne/projects/whisperseg"
source_dir="$base_dir"/data/data_backup
dest_dir="$base_dir"/data/lemur_setup
dest_name="moan_balanced_other"

# prep
rm -f $source_dir/finetune/* $source_dir/pretrain/*
cp $source_dir/source/original_7/* $source_dir/finetune
cp $source_dir/source/original_7/* $source_dir/pretrain
cp $source_dir/source/aug_3_curated/* $source_dir/finetune
cp $source_dir/source/aug_3_curated/* $source_dir/pretrain

python $base_dir/util/clean_tables.py -p $source_dir/finetune
python $base_dir/util/clean_tables.py -p $source_dir/pretrain
python $base_dir/util/make_json.py -p $source_dir/finetune -t 0.5 -d 2.5 -o $source_dir/finetune -a animal_filter_replace -f mo
python $base_dir/util/make_json.py -p $source_dir/finetune -t 0.5 -d 2.5 -o $source_dir/pretrain -a animal
python $base_dir/util/trim_wavs.py -p $source_dir/finetune
python $base_dir/util/trim_wavs.py -p $source_dir/pretrain
python $base_dir/util/balance_cuts.py -p $source_dir/finetune -s 30 -o $source_dir/finetune
python $base_dir/util/balance_cuts.py -p $source_dir/pretrain -s 30 -o $source_dir/pretrain

files=(
    "\(2019_03_15-12_02_11\)_CSWMUW240241_0000_first*"
    "\(2019_03_15-12_02_11\)_CSWMUW240241_0001_first*"
    "\(2021_01_17-03_53_54\)_ASWMUX209084_0003_first*"
    "\(2021_04_21-19_04_26\)_ASWMUX209084_0000_first*"
    "\(2023_10_05-09_05_06\)_ASWMUX208980_0017_second*"
    "\(2023_10_10-12_07_50\)_CSWMUW240241_0001_second*"
    "\(2023_10_18-10_06_01\)_ASWMUX209146_0024_second*"
)

cfg_count=1
for test_file in "${files[@]}"; do
    # reset lemur_setup to default
    rm -f "$dest_dir"/pretrain/*
    rm -f "$dest_dir"/finetune/*
    rm -f "$dest_dir"/test/*
    cp "$source_dir"/pretrain/*.json "$dest_dir"/pretrain/
    cp "$source_dir"/finetune/*.json "$dest_dir"/finetune/

    # split up test file
    mv "$dest_dir"/pretrain/$test_file "$dest_dir"/test
    mv "$dest_dir"/finetune/$test_file "$dest_dir"/test

    # create tar
    cd "$dest_dir"
    tar -cf "lemur_labels_cfg${cfg_count}_${dest_name}.tar" *
    mv "$dest_dir"/lemur_labels* "$base_dir/data/lemur_tar/labels_${dest_name}"
    ((cfg_count++))
done

cfg_count=1
for test_file in "${files[@]}"; do
    # reset lemur_setup to default
    rm -f "$dest_dir"/pretrain/*
    rm -f "$dest_dir"/finetune/*
    rm -f "$dest_dir"/test/*
    cp "$source_dir"/pretrain/*.wav "$dest_dir"/pretrain/
    cp "$source_dir"/finetune/*.wav "$dest_dir"/finetune/

    # split up test file
    mv "$dest_dir"/pretrain/$test_file "$dest_dir"/test
    mv "$dest_dir"/finetune/$test_file "$dest_dir"/test

    # create tar
    cd "$dest_dir"
    tar -cf "lemur_data_cfg${cfg_count}_${dest_name}.tar" *
    mv "$dest_dir"/lemur_data* "$base_dir/data/lemur_tar/data_${dest_name}"
    ((cfg_count++))
done