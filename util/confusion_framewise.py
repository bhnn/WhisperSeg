import argparse
import json
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix


def confusion_matrix_framewise(prediction: np.ndarray, label: np.ndarray, time_per_frame_for_scoring = 0.01, name: str = None):
    """Create a confusion matrix from frame-wise scores

    Args:
        prediction (np.ndarray): Numpy array containing predictions
        label (np.ndarray): Numpy array containing labels
        time_per_frame_for_scoring (float, optional): Bin-size for frame-wise scoring. Defaults to 0.01.
        name (str, optional): Used to pass job information so each job creates cms with unique names. Defaults to None.
    """
    prediction_segments = prediction
    label_segments = label

    prediction_segments["cluster"] = list( map(str, prediction_segments["cluster"]) )
    label_segments["cluster"] = list( map(str, label_segments["cluster"]) )

    cluster_to_id_mapper = {}
    for cluster in list(prediction_segments["cluster"]) + list(label_segments["cluster"]):
        if cluster not in cluster_to_id_mapper:
            cluster_to_id_mapper[cluster] = len( cluster_to_id_mapper )

    all_timestamps = list(prediction_segments["onset"]) + list(prediction_segments["offset"]) + \
                        list(label_segments["onset"]) + list( label_segments["offset"] )
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

    # sort both numerical and alphabetical labels by the alphabetical order
    labels_alpha, labels_num = zip(*sorted(zip(cluster_to_id_mapper.keys(), cluster_to_id_mapper.values())))
    labels_alpha = list(['#', *labels_alpha])
    labels_num = list([-1, *labels_num])

    # seaborn todo: add black line color to colorbar
    cm = confusion_matrix(
        y_true=frame_wise_label,
        y_pred=frame_wise_prediction,
        labels=labels_num,
        sample_weight=None,
        normalize=None,
    )
    scaler = 2
    _, ax = plt.subplots(1, 1, figsize=(6.4 * scaler, 4.8 * scaler))
    cm_annotations = [['' if x == 0 else f'{x:.0f}' for x in row] for row in cm]
    sns.heatmap(
        data=cm,
        # vmax=5000,
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
    ax.set_xlabel('Predicted label')
    ax.set_ylabel('True label')
    print(cm)
    print(classification_report(frame_wise_label, frame_wise_prediction, zero_division=np.nan, labels=labels_num, target_names=labels_alpha))
    if name != None:
        plt.savefig(f'/usr/users/bhenne/projects/whisperseg/results/{name}_cm_framewise.png', format='png', dpi=400, bbox_inches='tight')
    else:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(f'/usr/users/bhenne/projects/whisperseg/results/{current_time}_cm_framewise.png', format='png', dpi=400, bbox_inches='tight')
    # plt.savefig(r'D:\work\whisperseg\confusion_framewise.png', format='png', dpi=400, bbox_inches='tight')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a confusion matrix from frame-wise scores loaded from a file")
    parser.add_argument("--prediction_file", type=str, help="Path to file containing predictions", required=True)
    parser.add_argument("--label_file", type=str, help="Path to file containing labels", required=True)
    args = parser.parse_args()

    prediction = json.load(open(args.prediction_file))
    label = json.load(open(args.label_file))
    confusion_matrix_framewise(prediction, label, time_per_frame_for_scoring=0.001)