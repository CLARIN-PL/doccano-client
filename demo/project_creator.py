from doccano_client import DoccanoClient
import os
import jsonlines


DATA_DIR = './datasets'
LABEL_DIR = './labels_config'
DATA_FORMAT = 'JSON'
COLUMN_DATA ='text'
COLUMN_LABEL ='label'

USER_DATA = 'users.jsonl'
USER_ROLE = 'annotator'
PROJECT_TYPE = 'AffectiveAnnotation'

ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'password'
BASE_URL = 'http://localhost:8000'
ANNOTATION_MODES = ['OthersAnnotation', 'HumorAnnotation', 'OffensiveAnnotation', 'EmotionsAnnotation', 'SummaryAnnotation']

IS_MULTI_DIMENSION = True

LIST_DATA_FILES = os.listdir(DATA_DIR)
LIST_LABEL_FILES = os.listdir(LABEL_DIR)
LABELS_CONFIG_MAPPING = dict(zip(ANNOTATION_MODES[:-1], LIST_LABEL_FILES))

client = DoccanoClient(base_url=BASE_URL)
client.login(username=ADMIN_NAME, password=ADMIN_PASSWORD)


def create_users():
    list_users = []
    with open(USER_DATA, 'r') as f:
        for item in jsonlines.Reader(f):
            list_users.append(item['username'])
            try:
                client.create_user(username=item['username'], password=item['password'])
            except:
                pass
    print("Users created: {}".format(list_users))
    return list_users


def single_dimension_process(idx, annotation_mode, usernames):
    if annotation_mode=='SummaryAnnotation':
        client.create_project(name="{}_{}".format(LIST_DATA_FILES[idx].split('.')[0], annotation_mode), project_type=PROJECT_TYPE, description="Affective Annotation Summary mode", is_summary_mode=True, is_single_ann_view=True)
    elif annotation_mode=='EmotionsAnnotation':
        client.create_project(name="{}_{}".format(LIST_DATA_FILES[idx].split('.')[0], annotation_mode), project_type=PROJECT_TYPE, description="Affective Annotation Emotions mode", is_emotions_mode=True, is_single_ann_view=True)
    elif annotation_mode=='OffensiveAnnotation':
        client.create_project(name="{}_{}".format(LIST_DATA_FILES[idx].split('.')[0], annotation_mode), project_type=PROJECT_TYPE, description="Affective Annotation Offensive mode", is_offensive_mode=True, is_single_ann_view=True)
    elif annotation_mode=='HumorAnnotation':
        client.create_project(name="{}_{}".format(LIST_DATA_FILES[idx].split('.')[0], annotation_mode), project_type=PROJECT_TYPE, description="Affective Annotation Humor mode", is_humor_mode=True, is_single_ann_view=True)
    elif annotation_mode=='OthersAnnotation':
        client.create_project(name="{}_{}".format(LIST_DATA_FILES[idx].split('.')[0], annotation_mode), project_type=PROJECT_TYPE, description="Affective Annotation Others mode", is_others_mode=True, is_single_ann_view=True)

    current_project_id = list(client.list_projects())[-1].id
    client.upload(project_id=current_project_id, file_paths=[os.path.join(DATA_DIR, LIST_DATA_FILES[idx])], task=PROJECT_TYPE, format=DATA_FORMAT, column_data=COLUMN_DATA, column_label=COLUMN_LABEL)
    if annotation_mode!='SummaryAnnotation':
        client.upload_label_type(project_id=current_project_id, file_path=os.path.join(LABEL_DIR, LABELS_CONFIG_MAPPING[annotation_mode]), type='scale')
    for user in usernames:
        client.add_member(project_id=current_project_id, username=user, role_name=USER_ROLE)


def multi_dimension_process(idx, usernames):
    client.create_project(name="{}_{}".format(LIST_DATA_FILES[idx].split('.')[0], 'AffectiveAnnotation'), project_type=PROJECT_TYPE, description="Affective Annotation Multi-dimension mode", is_combination_mode=True, is_single_ann_view=True)
    current_project_id = list(client.list_projects())[-1].id
    client.upload(project_id=current_project_id, file_paths=[os.path.join(DATA_DIR, LIST_DATA_FILES[idx])], task=PROJECT_TYPE, format=DATA_FORMAT, column_data=COLUMN_DATA, column_label=COLUMN_LABEL)
    for file in LIST_LABEL_FILES:
        client.upload_label_type(project_id=current_project_id, file_path=os.path.join(LABEL_DIR, file), type='scale')
    for user in usernames:
        client.add_member(project_id=current_project_id, username=user, role_name=USER_ROLE)


def main():
    usernames = create_users()
    for idx in range(len(LIST_DATA_FILES)):
        if IS_MULTI_DIMENSION:
            multi_dimension_process(idx, usernames)
        else:
            for annotation_mode in ANNOTATION_MODES:
                single_dimension_process(idx, annotation_mode, usernames)
        print("Finished creating projects, users and uploading data, labels. Assigning users to projects...")

if __name__ == '__main__':
    main()
