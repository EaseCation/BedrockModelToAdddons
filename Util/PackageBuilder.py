# -*- coding: utf-8 -*-
import os
import json


# 用于创建文件夹的函数
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


# 用于生成预设文件的函数
def create_json_file(path, data):
    if not os.path.exists(path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"文件已生成：{path}")
        except Exception as e:
            print(f"创建文件 {path} 时发生错误: {e}")


def buildDirectories(base_path, directory):
    print("目录修正开始")

    # 定义目标文件夹路径
    folder_paths = [
        # behavior_pack
        os.path.join(base_path, "behavior_pack", "entities", directory),
        os.path.join(base_path, "behavior_pack", "netease_blocks"),
        # resource_pack
        os.path.join(base_path, "resource_pack", "entity", directory),
        os.path.join(base_path, "resource_pack", "models", "entity", directory),
        os.path.join(base_path, "resource_pack", "textures", "entity", directory)
    ]

    # 创建所有需要的目录
    for path in folder_paths:
        create_directory(path)

    # 目标文件路径
    blocks_json_path = os.path.join(base_path, "resource_pack", "blocks.json")
    item_texture_json_path = os.path.join(base_path, "resource_pack", "textures", "item_texture.json")
    terrain_texture_json_path = os.path.join(base_path, "resource_pack", "textures", "terrain_texture.json")

    # 预设的 JSON 内容
    blocks_data = {"format_version": [1, 1, 0]}
    item_texture_data = {
        "resource_pack_name": "vanilla",
        "texture_data": {},
        "texture_name": "atlas.items"
    }
    terrain_texture_data = {
        "resource_pack_name": "vanilla",
        "texture_data": {},
        "texture_name": "atlas.terrain"
    }

    # 创建所需的 JSON 文件
    create_json_file(blocks_json_path, blocks_data)
    create_json_file(item_texture_json_path, item_texture_data)
    create_json_file(terrain_texture_json_path, terrain_texture_data)

    print("目录修正结束")
