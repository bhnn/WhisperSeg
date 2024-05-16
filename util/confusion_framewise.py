import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix


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

    # labels_alpha, labels_num = zip(*sorted(zip(cluster_to_id_mapper.keys(), cluster_to_id_mapper.values())))
    labels_alpha = list(['#', *cluster_to_id_mapper.keys()])
    labels_num = list([-1, cluster_to_id_mapper.values()])

    # scaler = 1.5
    # _ = plt.figure(figsize=(6.4 * scaler, 4.8 * scaler))
    # cm = ConfusionMatrixDisplay.from_predictions(
    #     y_true=frame_wise_label,
    #     y_pred=frame_wise_prediction,
    #     labels=labels_num,
    #     display_labels=labels_alpha,
    #     # values_format='.2g',
    #     sample_weight=None,
    #     normalize=None,
    #     cmap='viridis',
    #     xticks_rotation='horizontal',
    # )
    # plt.tight_layout()
    # fig = plt.gcf()
    # print(fig.get_size_inches())

    # seaborn todo: add black line color to colorbar
    cm = confusion_matrix(
        y_true=frame_wise_label,
        y_pred=frame_wise_prediction,
        sample_weight=None,
        normalize=None,
    )
    scaler = 3
    _, ax = plt.subplots(1, 1, figsize=(6.4 * scaler, 4.8 * scaler))
    cm_annotations = [['' if x == 0 else f'{x}' for x in row] for row in cm]
    sns.heatmap(
        data=cm,
        vmax=5000,
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
    plt.yticks(rotation=0)
    ax.set_xlabel('Predicted label')
    ax.set_ylabel('True label')
    print(labels_alpha)
    print(classification_report(frame_wise_label, frame_wise_prediction, zero_division=np.nan))
    plt.savefig('/usr/users/bhenne/projects/whisperseg/confusion_framewise.png', format='png', dpi=400, bbox_inches='tight')