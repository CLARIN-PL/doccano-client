from doccano_client import DoccanoClient
from doccano_client.models.project import Project
from doccano_client.repositories.project import ProjectRepository

import os
import random
import pandas as pd
import json
import jsonlines

client = DoccanoClient('http://localhost:8000')
client.login(username='admin', password='password')
# client.get_profile()

DATA_DIR = 'dynamic_ann_proj_data/'
JSON_EXAMPLE_DIR = 'dynamic_ann_proj_data/json_examples/'

LABEL_DIR = './labels_config'
LIST_LABEL_FILES = os.listdir(LABEL_DIR)

DATA_FORMAT = 'JSON'
COLUMN_DATA ='text'
COLUMN_LABEL ='label'

USER_DATA = 'users.jsonl'
USER_ROLE = 'annotator'

PROJECT_TYPE = 'DynamicAnnotation'

# ADMIN_LIST = ['acandri', 'piotrmilkowski', 'tferdinan', str(5635), str(6198), str(1238), str(1163)]
ADMIN_LIST = [str(5635), str(6198), str(1238), str(1163)]

ADMIN_ROLE = 'project_admin'

ANNOTATION_MODES = ['OthersAnnotation', 'HumorAnnotation', 'OffensiveAnnotation', 'EmotionsAnnotation', 'SummaryAnnotation']

def create_json_example_files(data_dir, json_example_dir):
    text_df = pd.read_csv(os.path.join(data_dir, 'texts.csv'))
    text_df = text_df.rename(columns={'order_in_project': 'order', 'text_type': 'type'})
    text_df['article_id'] = "default"
    text_df['meta'] = text_df[['article_id']].to_dict(orient='records')
    res = text_df.groupby('project_id')
    for idx in list(text_df.project_id.unique()):
        res_dict = res.get_group(idx)[['text', 'type', 'article_id', 'order', 'meta']].to_dict('records')
        res_dict = [dict(item, scale=[]) for item in res_dict]
        res_dict = [dict(item, label=[]) for item in res_dict]
        with open(os.path.join(json_example_dir, "examples_project_{}.json".format(idx)), "w") as file:
            json.dump(res_dict, file)
            
def pre_process_project_data(data_dir):
    project_df = pd.read_csv(os.path.join(data_dir, 'projects.csv'))
    project_df = project_df.rename(columns={'Mnie bawi/śmieszy?': 'Bawi/śmieszny mnie'})
    list_dimensions = project_df.columns.to_list()[2:]
    databasse_dynamic_dimensions_df = pd.read_csv(os.path.join(data_dir, 'projects_dynamicdimension.csv'))
    dim_mapping = {}
    for dim in list_dimensions:
        if dim in databasse_dynamic_dimensions_df.name.to_list():
            dim_mapping.update({dim: int(databasse_dynamic_dimensions_df[databasse_dynamic_dimensions_df['name']==dim].id)})
    project_df = project_df.rename(columns=dim_mapping)
    new_dim_ls = project_df.columns.to_list()[2:]
    new_project_df = project_df.apply(lambda x: [{"dimension": [col]} for col in new_dim_ls if x[col] == 1], axis=1)
    return new_project_df, project_df

def multi_dimension_process(idx, dimension_list, usernames, admins, json_data_dir, package_data_type):
    created_project = client.create_project(name="{}_project_{}".format('DynamicDimension', idx), project_type=PROJECT_TYPE, description="Dynamic dimension project",       is_combination_mode=True, is_single_ann_view=True, dimension=dimension_list, package_data_type=package_data_type)
    current_project_id = created_project.id
    client.upload(project_id=current_project_id, file_paths=[os.path.join(json_data_dir, "examples_project_{}.json".format(idx))], task=PROJECT_TYPE, format=DATA_FORMAT, column_data=COLUMN_DATA, column_label=COLUMN_LABEL)
    for file in LIST_LABEL_FILES:
        client.upload_label_type(project_id=current_project_id, file_path=os.path.join(LABEL_DIR, file), type='scale')
    for user in usernames:
        client.add_member(project_id=current_project_id, username=str(user), role_name=USER_ROLE)
    if admins:
        for admin in admins:
            client.add_member(project_id=current_project_id, username=admin, role_name=ADMIN_ROLE)
            
def main():
    # usernames = create_users()
    file = open(os.path.join(DATA_DIR, "users_detached.txt"), "r")
    lines = file.readlines()
    list_usernames = [user.split('\n')[0] for user in lines]

    # create_json_example_files(data_dir=DATA_DIR, json_example_dir=JSON_EXAMPLE_DIR)
    
    new_project_df, project_df = pre_process_project_data(data_dir=DATA_DIR)
    for idx in new_project_df.index.to_list():
        dimension_list = new_project_df[idx]
        current_project_type = int(project_df[project_df['project_id']==idx].project_type)
        if current_project_type==0:
            package_flag = False
        else:
            package_flag = True
        multi_dimension_process(idx, dimension_list=dimension_list, usernames=list_usernames, admins=ADMIN_LIST, json_data_dir=JSON_EXAMPLE_DIR, package_data_type=package_flag)
        print("Finished creating projects, users and uploading data, labels. Assigning users to projects...")

if __name__ == '__main__':
    main()
