import argparse
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix
from common import get_flex_file_iterator
import json


def confusion_matrix_framewise(prediction: np.ndarray, label: np.ndarray, cluster_to_id_mapper: dict):
    """Create a confusion matrix from frame-wise scores

    Args:
        prediction (np.ndarray): Numpy array containing predictions
        label (np.ndarray): Numpy array containing labels
        time_per_frame_for_scoring (float, optional): Bin-size for frame-wise scoring. Defaults to 0.01.
    """
    # sort both numerical and alphabetical labels by the alphabetical order
    labels_alpha, labels_num = zip(*sorted(zip(cluster_to_id_mapper.keys(), cluster_to_id_mapper.values())))
    labels_alpha = list(['Background', *labels_alpha])
    labels_num = list([-1, *labels_num])
    
    labels_alpha = [l if l != 'mo' else 'moan' for l in labels_alpha]

    # seaborn todo: add black line color to colorbar
    cm = confusion_matrix(
        y_true=label,
        y_pred=prediction,
        labels=labels_num,
        sample_weight=None,
        normalize='true',
    )
    scaler = 2
    _, ax = plt.subplots(1, 1, figsize=(6.4 * scaler, 4.8 * scaler))
    # cm_annotations = [['' if x == 0 else f'{x:.0f}' for x in row] for row in cm]
    # cm_annotations = [['' if x == 0 else f'{x:.3f}' for x in row] for row in cm]
    cm_annotations = [[f'{x:.3f}' for x in row] for row in cm]
    # cm_annotations = [['' if x < 0.01 else f'{x:.3f}' for x in row] for row in cm]
    sns.set(font_scale=1.1)
    sns.heatmap(
        data=cm,
        # vmax=580000,
        cmap='viridis',
        annot=cm_annotations,
        fmt='',
        square=True,
        linewidths=.25,
        linecolor='#222',
        xticklabels=labels_alpha,
        yticklabels=labels_alpha,
        ax=ax,
    )
    # plot adjustments
    plt.yticks(rotation=0)
    ax.set_xlabel('Predicted label', fontsize=16)
    ax.set_ylabel('True label', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=14)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    # plt.savefig(f'/usr/users/bhenne/projects/whisperseg/results/{current_time}_cm_framewise.pdf', format='pdf', dpi=400, bbox_inches='tight')
    plt.savefig(f'D:\\work\\whisperseg\\results\\{current_time}_cm_framewise.pdf', format='pdf', dpi=400, bbox_inches='tight')

def gather_predictions(data_path: str, time_per_frame_for_scoring=0.001, **kwargs) -> (tuple[list[np.ndarray], list[np.ndarray], dict]):
    """Gather predictions and labels from all cmraw files in the data_path

    Args:
        data_path (str): Path to the data
        time_per_frame_for_scoring (float, optional): Bin-size for frame-wise scoring. Defaults to 0.001.

    Raises:
        ValueError: If unexpected annotations are found

    Returns:
        (tuple[list[np.ndarray], list[np.ndarray], dict]): List of frame-wise predictions, list of frame-wise labels, and
        a dictionary mapping annotations to ids
    """
    frame_wise_labels = []
    frame_wise_predictions = []
    cluster_to_id_mapper = {}
    annotations = []
    # first pass of all files: construct annotation to id mapping for all present annotations
    for file in get_flex_file_iterator(data_path, rglob_str='*.cmraw'):
        with open(file, 'r') as f:
            cmdata = json.load(f)
        prediction_segments = cmdata["prediction"]
        label_segments = cmdata["label"]

        annotations.extend(list( map(str, prediction_segments["cluster"]) ))
        annotations.extend(list( map(str, label_segments["cluster"])))
    for cluster in annotations:
        if cluster not in cluster_to_id_mapper:
            cluster_to_id_mapper[cluster] = len( cluster_to_id_mapper)

    # second pass of all files: construct prerequisites for cms based on universal annotation mapping
    for file in get_flex_file_iterator(data_path, rglob_str='*.cmraw'):
        with open(file, 'r') as f:
            cmdata = json.load(f)
        prediction_segments = cmdata["prediction"]
        label_segments = cmdata["label"]

        prediction_segments["cluster"] = list( map(str, prediction_segments["cluster"]) )
        label_segments["cluster"] = list( map(str, label_segments["cluster"]) )
        # if set() != (missing := set(cluster_to_id_mapper.keys()) ^ set(list(prediction_segments["cluster"]) + list(label_segments["cluster"]))):
        #     raise ValueError(f"Unexpected annotations \"{missing}\" found.")     
        if not (superset := set(cluster_to_id_mapper.keys())).issuperset(subset := set(list(prediction_segments["cluster"]) + list(label_segments["cluster"]))):
            raise ValueError(f"Unexpected annotations \"{superset.difference(subset)}\" found.") 

        all_timestamps = list(prediction_segments["onset"]) + list(prediction_segments["offset"]) + list(label_segments["onset"]) + list( label_segments["offset"] )
        if len(all_timestamps) == 0:
            max_time = 1.0
        else:
            max_time = np.max( all_timestamps )

        num_frames = int(np.round( max_time / time_per_frame_for_scoring )) + 1

        frame_wise_prediction = np.ones( num_frames ) * -1
        for idx in range( len( prediction_segments["onset"] ) ):
            onset_pos = int(np.round( prediction_segments["onset"][idx] / time_per_frame_for_scoring ))
            offset_pos = int(np.round( prediction_segments["offset"][idx] / time_per_frame_for_scoring ))
            frame_wise_prediction[onset_pos:offset_pos] = cluster_to_id_mapper[ prediction_segments["cluster"][idx] ]

        frame_wise_label = np.ones( num_frames ) * -1
        for idx in range( len( label_segments["onset"] ) ):
            onset_pos = int(np.round( label_segments["onset"][idx] / time_per_frame_for_scoring ))
            offset_pos = int(np.round( label_segments["offset"][idx] / time_per_frame_for_scoring ))
            frame_wise_label[onset_pos:offset_pos] = cluster_to_id_mapper[ label_segments["cluster"][idx] ]
        
        frame_wise_predictions.append(frame_wise_prediction)
        frame_wise_labels.append(frame_wise_label)
    return frame_wise_predictions, frame_wise_labels, cluster_to_id_mapper

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Builds a single confusion matrix from the results of a whole experiment across all data configs.")
    parser.add_argument("-d", "--data_path", type=str, help="Path to the data", required=True)
    parser.add_argument("-o", "--output_dir", type=str, help="Path to a directory where the output file will be saved", default=None)
    args = parser.parse_args()

    pred, true, id_mapper = gather_predictions(**vars(args))
    confusion_matrix_framewise(
        prediction=[p for sublist in pred for p in sublist],
        label=[l for sublist in true for l in sublist],
        cluster_to_id_mapper=id_mapper) # doesnt pass output_dir currently