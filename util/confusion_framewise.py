import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score


def confusion_matrix_framewise(prediction, label, target_cluster = None, time_per_frame_for_scoring = 0.01 ):
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
        normalize='all',
    )
    scaler = 2
    _, ax = plt.subplots(1, 1, figsize=(6.4 * scaler, 4.8 * scaler))
    cm_annotations = [['' if x == 0 else f'{x:.3f}' for x in row] for row in cm]
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

    # print(classification_report(frame_wise_label, frame_wise_prediction, zero_division=np.nan, target_names=labels_alpha))
    # print(classification_report(frame_wise_label, frame_wise_prediction, zero_division=np.nan, labels=labels_num, target_names=labels_alpha))
    # print(precision_score(y_true=frame_wise_label, y_pred=frame_wise_prediction, average='macro', zero_division=0))
    # print(precision_score(y_true=frame_wise_label, y_pred=frame_wise_prediction, average='weighted', zero_division=0))
    # plt.show()
    plt.savefig('/usr/users/bhenne/projects/whisperseg/confusion_framewise.png', format='png', dpi=400, bbox_inches='tight')
    # plt.savefig(r'D:\work\whisperseg\confusion_framewise.png', format='png', dpi=400, bbox_inches='tight')

if __name__ == "__main__":
    import json
    prediction = json.load(open(r'd:\Dropbox\pred.txt'))
    label = json.load(open(r'd:\Dropbox\true.txt'))
    confusion_matrix_framewise(prediction, label, time_per_frame_for_scoring=0.001)