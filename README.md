# Thesis project: Automatic Detection, Segmentation and Classification of Lemur Vocalisations

This repository contains the codebase of my thesis on detecting, segmenting and classifying *Lemur catta* vocalisations in outdoor audio recordings. It is a fork of the original [WhisperSeg](https://github.com/nianlonggu/WhisperSeg) model by Gu et al., as proposed in [their recent paper](https://ieeexplore.ieee.org/document/10447620).

## Content

- [Installation](#installation)
- [Execution](#execution)
- [Reproducing experiments](#reproducing-experiments)

## Installation

### Option 1: Install using anaconda/miniconda family

```bash
conda env create -f environment.yml
```

### Option 2: Install manually using pip

Linux:

```bash
conda create -n wseg python=3.10 -y
conda activate wseg
pip install -r requirements.txt
conda install -c pypi cudnn -y
```

Windows:

```bash
conda create -n wseg python=3.10 -y
conda activate wseg
pip install -r requirements_windows.txt
conda install -c pypi cudnn -y
```

## Execution

### Data Preparation

In order to train a new model, first a set of data files must be prepared. To start, split `.wav` audio files in halves using [split_wavs.py](/util/split_wavs.py). Move the resulting splits into a new directory (currently saved in same directory).

```python
python util/split_wavs.py --path path/to/data
```

Next, annotate the split recordings using [Raven Pro/Lite](https://www.ravensoundsoftware.com/) and place Raven selection tables into the same folder. The assumed naming convention for further processing is `<.wav_file>.Table.1.selections.txt`.

Then proceed with running the code for table cleaning, converting to `.json` and trimming of unannotated audio from the front and back of the files. This will also split the results into pretraining and finetuning, into separate folders.

```python
python util/clean_tables.py --path path/to/data/

# duplicate data, as trimming alters files in-place
mkdir -p pretrain finetune
cp path/to/data/ pretrain
cp path/to/data/ finetune

python util/make_json.py --file_path ./pretrain --output_path ./pretrain
python util/make_json.py --file_path ./finetune --output_path ./finetune
python util/trim_wavs.py --file_path ./pretrain
python util/trim_wavs.py --file_path ./finetune
```

Refer to [make_json.py](/util/make_json.py) for switches to modify `tolerance` or `clip_duration` values or for ways to filter and convert annotations (e.g. single calls, merging targets).

### Training and Evaluation

Using the prepared data, models can now be trained. This process consists of a pretraining and a finetuning step. Gu et al. recommend using their model checkpoints with a multi-species pretraining history for enhanced effectiveness. These are available for the [Whisper-Base](https://huggingface.co/nccratliri/whisperseg-base-animal-vad-ct2) and [Whisper-Large](https://huggingface.co/nccratliri/whisperseg-animal-vad-ct2) model architectures and are automatically downloaded when running the model using their *huggingface* designation. For this, execute the following commands after each other. Each step may take some time, depending on your compute resources.

```python
python train.py \
  --initial_model_path nccratliri/whisperseg-base-animal-vad \
  --train_dataset_folder path/to/pretrain_data \
  --model_folder path/to/save_trained_model \
  --gpu_list 0 \
  --max_num_epochs 10 \

python train.py \
  --initial_model_path path/to/<pretrained_model>/final_checkpoint \
  --train_dataset_folder path/to/finetune_data \
  --model_folder path/to/save_trained_model \
  --gpu_list 0 \
  --max_num_epochs 10 \
```

If you have file(s) set aside for testing, you can evaluate the model's segmentation performance by running

```python
python evaluate.py \
  --dataset_path path/to/test_data \
  --model_path path/to/<finetuned_model>/final_checkpoint_ct2 \
  --output_dir path/to/results_dir
```

For shell scripts that run these steps for you, refer to [train_base.sh](/jobs/train_large.sh), [evaluate_large.sh](jobs/evaluate_large.sh) and [infer_large.sh](/jobs/infer_large.sh). These scripts were written for a SLURM-controlled HPC environment and will handle moving data to a working directory, fully training a model, evaluating it and cleaning up after themselves. If you do not have access to such an environment, they will nonetheless be helpful to understand the training process.

More in-depth explanations of data processing, model training and evaluation can be found in the documentation of the original *WhisperSeg* implementation by Gu et al. ([here](https://github.com/nianlonggu/WhisperSeg?tab=readme-ov-file#model-training-and-evaluation) and [here](https://github.com/nianlonggu/WhisperSeg/tree/master/docs)).

## Reproducing experiments

The code to reproduce all experiments in the thesis can be found in [jobs](/jobs/). Experiments that rely on a specific preparation of the data come with a `prepare_<exp>.sh` script that will process data into the required state. Otherwise, each experiment consists of one or more `job_<exp>.sh` files (e.g. for rtx5000 vs v100) and a `run_<exp>.sh` file that sends a number of these jobs to the HPC controller.

Experiments:

- Baseline-Pre: [Link](/jobs/experiment_baseline_pre/)
- Batchsize & Learning rate: [Link](/jobs/experiment_bslr/)
- Patience: [Link](/jobs/experiment_patience/)
- Validation ratio: [Link](/jobs/experiment_vratio/)
- Tolerance: [Link](/jobs/experiment_tolerance/)
- Clip duration: [Link](/jobs/experiment_clipd/)
- Call / no-call: [Link](/jobs/experiment_yesno/)
- Single call: [Link](/jobs/experiment_single_call/)
- 9 calls: [Link](/jobs/experiment_9call/)
- Additional pretraining: [Link](/jobs/experiment_pre_parent/)
- Class balancing: [Link](/jobs/experiment_balanced/)
- Strategy augmentation: [Link](/jobs/experiment_single_call_balanced/)
- 7+3 Un/Curated: [Link](/jobs/experiment_augmentation/)
- 7+150: [Link](/jobs/experiment_aug150/)

## Acknowledgements

- Nianlong Gu, for his kind assistance with questions about the original codebase
