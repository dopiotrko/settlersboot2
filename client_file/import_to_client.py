import wx
import logging
import os
import json
import my
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')


def open_import_destination_folder():
    logging.info('open_import_destination_folder')
    app = wx.App()
    dlg = wx.DirDialog(
        None, message="Choose a directory",
        defaultPath=os.getcwd() + '/data',
        style=wx.DD_DEFAULT_STYLE
    )
    path = None
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    dlg.Destroy()
    return path


def save_json(path, json_data):
    logging.info('save_json:')
    with open(path, 'w') as f:
        json.dump(json_data, f, indent=2)


def open_data_to_import():
    logging.info('open_data_to_import')
    app = wx.App()
    dlg = wx.FileDialog(
        None, message="Open data to import",
        defaultDir=os.getcwd(),
        defaultFile="",
        # wildcard="Adventure file (*.data)|*.data",
        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW
    )
    data = None
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
        with open(path, encoding='utf8') as f:
            data = json.load(f)
    dlg.Destroy()
    return data


def group_generals_by_id(my_generals_):
    generals = {}
    for general_id, general_data in my_generals_.items():
        general_type = general_data["type"]
        added_generals_of_this_type = generals.get(general_type, [])
        added_generals_of_this_type.append(general_id)
        generals.update({general_type: added_generals_of_this_type})
    return generals


def replace_generals_ids(imported_data):
    imported_generals = imported_data['generals']
    with open(os.getcwd() + '/resource/generals.json', encoding='utf8') as f:
        my_generals = json.load(f)
    my_generals_by_id = group_generals_by_id(my_generals)
    old_new_generals_substitute = {}
    updated_generals = {}
    for general_id, general_description in imported_generals.items():
        new_general_id = my_generals_by_id[general_description['type']].pop(0)
        old_new_generals_substitute.update({general_id: new_general_id})
        updated_generals.update({new_general_id: general_description})
    updated_content = {}
    for stage_file_name, stage_content in imported_data['content'].items():
        updated_stage = {}
        for general_id, general_content in stage_content.items():
            new_general_id = old_new_generals_substitute[general_id]
            general_content.update({'name': my_generals[new_general_id]['name']})
            updated_stage.update({new_general_id: general_content})
        updated_content.update({stage_file_name.replace('txt', 'json'): updated_stage})
    return updated_content


def add_path_to_items(imported_data, import_destination_folder_):
    tree = imported_data['tree']
    for item in tree['items']:
        if isinstance(item, list):
            item[0] = import_destination_folder_ + '\\' + item[0].replace('txt', 'json')
    return tree


settings_path = 'C:/Users/dopiotrko/AppData/Local/Ubisoft/The Settlers Online/'
imported_data_ = open_data_to_import()
print(os.getcwd())
content = replace_generals_ids(imported_data_)
with open(settings_path + 'settings.json', encoding='utf8') as f:
    data = json.load(f)
# save backup
save_json(my.get_new_filename('settings', settings_path + '{}'), data)
import_destination_folder = open_import_destination_folder()
for file_name, file_content in content.items():
    save_json(import_destination_folder + '\\' + file_name, file_content)
data['shortcuts'].append(add_path_to_items(imported_data_, import_destination_folder))
save_json(settings_path + 'settings.json', data)
print(data)
# print(adv)
