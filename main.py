# -*- coding: utf-8 -*-
import json
import shutil
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from googletrans import Translator
import Util.PackageBuilder as PackageBuilder
import Presets.behaviorPresets as behaviorPresets
import copy


def subNameByPath(path, txtList):
    """
    批量删除文件名中包含的子串

    参数:
        path (str): 目标文件夹路径
        txtList (list): 需要删除的子串列表
    """
    # 遍历指定目录下的所有文件
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        if os.path.isdir(file_path):
            continue

        # 对每个 txtList 中的子串进行替换
        new_filename = filename
        for txt in txtList:
            if txt in new_filename:
                new_filename = new_filename.replace(txt, '')

        # 如果文件名发生了变化，执行重命名操作
        if new_filename != filename:
            new_file_path = os.path.join(path, new_filename)
            if not os.path.exists(new_file_path):
                os.rename(file_path, new_file_path)


# 批量修改文件名
def renameAddByPath(path, prefix, suffix, directoryType):

    try:
        # 获取目录中的所有文件和子目录
        entries = os.listdir(path)

        # 遍历目录中的每一项
        for entry in entries:
            full_path = os.path.join(path, entry)

            # 仅处理文件，忽略目录
            if os.path.isfile(full_path):
                # 分离文件名和扩展名
                file_name, file_extension = os.path.splitext(entry)
                # 构建新的文件名
                file_name = file_name.replace(".geo", "")
                if directoryType == "geo":
                    new_filename = f"{prefix}{file_name}{suffix}.geo{file_extension}"
                else:
                    new_filename = f"{prefix}{file_name}{suffix}{file_extension}"
                new_path = os.path.join(path, new_filename)

                # 重命名文件
                os.rename(full_path, new_path)
                print(f"规范化命名: {entry} -> {new_filename}")

    except Exception as e:
        print(f"发生错误: {e}")

# 批量翻译文件名
def nameTranslateByDirectory(path):
    # 初始化翻译器
    translator = Translator()

    # 遍历目录中的文件
    for filename in os.listdir(path):
        # 跳过非文件
        if not os.path.isfile(os.path.join(path, filename)):
            continue

        # 分离文件名和扩展名
        file_name, file_extension = os.path.splitext(filename)

        try:
            # 翻译文件名
            translated_name = translator.translate(file_name, src='auto', dest='zh-cn').text

            # 创建新文件名
            new_filename = f"{file_name}_{translated_name}{file_extension}"

            # 重命名文件
            os.rename(
                os.path.join(path, filename),
                os.path.join(path, new_filename)
            )
            print(f"Renamed: {filename} -> {new_filename}")
        except Exception as e:
            print(f"Error renaming file {filename}: {e}")

# 批量修改geo中的identifier
def modifyGeoIdentifier(path):
    """
    遍历目录，打开所有 .json 文件，并修改其中的 identifier 值。

    参数:
        directory (str): 目标目录路径
    """

    def update_identifier(data, filename_base):
        """
        递归地更新数据中 key 为 'identifier' 的值。
        如果值是字符串，更新为 'geometry.' + 文件名去掉 '.geo' 和扩展名的部分。
        如果值是字典，则深入查找并递归修改。

        参数:
            data (dict or list): JSON 数据
            filename_base (str): 用于拼接 'geometry.' 前缀的基础文件名

        返回:
            更新后的数据
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "identifier":
                    if isinstance(value, str):
                        data[key] = f"geometry.{filename_base}"
                else:
                    update_identifier(value, filename_base)
        elif isinstance(data, list):
            for item in data:
                update_identifier(item, filename_base)
        return data
    try:
        # 遍历目录下的所有文件
        for filename in os.listdir(path):
            if filename.endswith(".json"):
                full_path = os.path.join(path, filename)

                # 提取基础文件名，去掉 .geo 和扩展名部分
                filename_base = os.path.splitext(filename)[0].replace(".geo", "")

                # 打开 JSON 文件并读取内容
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 更新 identifier 值
                updated_data = update_identifier(data, filename_base)

                # 将修改后的数据写回文件
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_data, f, indent=4, ensure_ascii=False)

                print(f"已修正Geometry名称: {filename}")

    except Exception as e:
        print(f"发生错误: {e}")

# 批量生成生物行为包
def buildBehaviorEntityByDirectory(input_directory, output_directory):
    """
    批量读取指定目录下的 JSON 文件，通过调用行为生成方法，
    并将生成的行为数据字典保存到指定的输出目录。

    参数:
        input_directory (str): 输入目录路径，包含需要处理的 JSON 文件。
        output_directory (str): 输出目录路径，用于保存生成的 JSON 文件。
    """
    def buildDemo(filename_base):
        """
        根据文件名基础部分生成生物行为的字典数据。
        模拟了生成行为组件的过程，实际应用中此部分可以根据具体需求更改。

        参数:
            filename_base (str): 文件名（去掉扩展名部分）

        返回:
            dict: 包含生物行为和组件的字典数据
        """
        # 示例生成的字典内容，模拟生成某种实体的行为数据
        behavior_data = copy.deepcopy(behaviorPresets.entityDemo)
        behavior_data["minecraft:entity"]["description"]["identifier"] = "{}:{}".format(config["name"], filename_base)
        return behavior_data
    try:
        # 遍历输入目录中的所有文件
        for filename in os.listdir(input_directory):

            # 获取文件名基础部分（去掉扩展名）
            filename_base = os.path.splitext(filename)[0]

            # 生成行为数据字典
            result_dict = buildDemo(filename_base)

            # 构建输出文件路径
            output_file_path = os.path.join(output_directory, f"{filename_base}.json")

            # 将字典数据保存为 JSON 文件
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=4, ensure_ascii=False)

            print(f"已生成行为数据{filename_base}.json并保存到: {output_file_path}")
    except Exception as e:
        print(f"发生错误: {e}")

# 批量生成方块行为包

def buildBehaviorBlockByDirectory(input_directory, output_directory):
    """
    批量生成方块行为包。

    遍历输入目录中的 JSON 文件，调用 generateBlockBehavior 方法生成行为字典，
    并将生成的字典保存到指定的输出目录。

    参数:
        input_directory (str): 输入目录路径，包含待处理的 JSON 文件。
        output_directory (str): 输出目录路径，用于保存生成的行为包 JSON 文件。
        config (dict): 配置信息，用于调整行为包命名规则等。
    """

    def generateBlockBehavior(filename_base):
        """
        根据文件名基础部分生成方块的行为字典。

        参数:
            filename_base (str): 文件名基础部分（不含扩展名）。

        返回:
            dict: 方块行为的字典。
        """
        # 生成方块行为的字典内容
        behavior = copy.deepcopy(behaviorPresets.blockDemo)
        behavior["minecraft:block"]["description"]["identifier"] = "{}:{}".format(config["name"], filename_base)
        return behavior

    # 确保输出目录存在
    os.makedirs(output_directory, exist_ok=True)

    try:
        # 遍历输入目录中的所有文件
        for filename in os.listdir(input_directory):
            # 获取去除扩展名后的文件基础部分
            filename_base = os.path.splitext(filename)[0]

            # 替换后缀，以便为方块生成合适的名称
            filename_base = filename_base.replace(config["suffix_entity"], config["suffix_block"])

            # 生成行为字典
            behavior_dict = generateBlockBehavior(filename_base)

            # 构建输出文件路径
            output_file_path = os.path.join(output_directory, f"{filename_base}.json")

            # 将字典保存为 JSON 文件
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                json.dump(behavior_dict, output_file, indent=4, ensure_ascii=False)

            # 输出生成的信息
            print(f"已生成netease_blocks输出到: {output_file_path}")

    except Exception as e:
        print(f"发生错误: {e}")


# 批量生成生物资源包
def buildResourceBlockByDirectory(input_directory, output_directory, path):
    """
    读取指定目录下的 JSON 文件名，调用 ABC 方法生成字典，
    并将生成的字典保存到指定的输出目录。

    参数:
        input_directory (str): 输入目录路径，包含 JSON 文件。
        output_directory (str): 输出目录路径，用于保存结果文件。
    """

    def buildBehavior(filename_base):
        # 示例生成的字典内容
        demo = {
                "format_version": "1.10.0",
                "minecraft:client_entity": {
                    "description": {
                        "geometry": {
                            "default": "geometry.{}".format(filename_base)
                        },
                        "identifier": "{}:{}".format(config["name"], filename_base),
                        "materials": {
                            "default": "entity_alphatest"
                        },
                        "render_controllers": [
                            "controller.render.default"
                        ],
                        "spawn_egg": {
                            "texture": "{}.egg".format(filename_base),
                            "texture_index": 0
                        },
                        "textures": {
                            "default": "textures/entity/{}/{}".format(path, filename_base)
                        }
                    }
                }
            }
        return demo
    # 如果输出目录不存在，创建目录
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    try:
        # 遍历输入目录中的所有文件
        for filename in os.listdir(input_directory):
            # if filename.endswith(".json"):
            # 去掉扩展名，获取文件名基础部分
            filename_base = os.path.splitext(filename)[0]
            # filename_base = filename_base.replace("_entity", "")
            # 调用 ABC 方法，生成字典
            result_dict = buildBehavior(filename_base)
            # 构建输出文件路径
            output_file_path = os.path.join(output_directory, f"{filename_base}.json")
            # 将字典保存为 JSON 文件
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=4, ensure_ascii=False)

            print(f"已根据: {filename} -> 生成资源包Entity输出到: {output_file_path}")

        print("所有文件处理完成！")
    except Exception as e:
        print(f"发生错误: {e}")

# 调整blocks.json文件(方块定义)
def buildBlocksJson(blocksPath, directory):
    """
    读取路径1中的 blocks.json 文件，获取路径2中的文件名，调用 ABC 进行处理，
    并将处理结果保存到 blocks.json 中。

    参数:
        path1 (str): 路径1目录，包含 blocks.json 文件。
        path2 (str): 路径2目录，包含待处理的文件。
    """

    def buildDemo(filename_base):
        # 示例生成的字典内容
        return {
        "client_entity": {
            "hand_model_use_client_entity": True,
            "identifier": "{}:{}".format(config["name"], filename_base),
            "block_icon": "{}:{}".format(config["name"], filename_base).replace(config["suffix_entity"], config["suffix_block"])
        },
        "sound": "metal"
    }

    # 读取路径1中的 blocks.json 文件
    blocks_json_path = os.path.join(blocksPath, "blocks.json")
    try:
        with open(blocks_json_path, 'r', encoding='utf-8') as f:
            blocks_data = json.load(f)
        print(f"成功读取 {blocks_json_path}")
    except Exception as e:
        print(f"读取 {blocks_json_path} 时发生错误: {e}")
        return

    # 获取路径2中的所有文件名，去掉扩展名
    filenames = [os.path.splitext(f)[0] for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    print(f"从目标路径中获取到 {len(filenames)} 个文件：{filenames}")

    # 调用 ABC 方法处理每个文件名，并将结果保存到 blocks_data 中
    for filename_base in filenames:
        result_dict = buildDemo(filename_base)
        blocks_data["{}:{}".format(config["name"], filename_base.replace(config["suffix_entity"], config["suffix_block"]))] = (result_dict)  # 将处理结果追加到 blocks_data

    # 保存处理后的数据回 blocks.json 文件
    try:
        with open(blocks_json_path, 'w', encoding='utf-8') as f:
            json.dump(blocks_data, f, indent=4, ensure_ascii=False)
        print(f"成功更新blocks.json到 {blocks_json_path}")
    except Exception as e:
        print(f"保存到 {blocks_json_path} 时发生错误: {e}")

    except Exception as e:
        print(f"发生错误: {e}")

# 调整item_texture.json文件(实体怪物蛋)
def buildItemTextureJson(itemTexturePath, directory):

    def buildDemo(filename_base):
        # 示例生成的字典内容
        return {
            "textures": "textures/items/egg/{}".format(filename_base)
        }

    # 读取路径1中的 item_texture.json 文件
    item_texture_json_path = os.path.join(itemTexturePath, "item_texture.json")
    try:
        with open(item_texture_json_path, 'r', encoding='utf-8') as f:
            item_texture_data = json.load(f)
        print(f"成功读取 {item_texture_json_path}")
    except Exception as e:
        print(f"读取 {item_texture_json_path} 时发生错误: {e}")
        return

    # 获取路径2中的所有文件名，去掉扩展名
    filenames = [os.path.splitext(f)[0] for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    print(f"从目标路径中获取到 {len(filenames)} 个文件：{filenames}")

    # 调用 ABC 方法处理每个文件名，并将结果保存到 blocks_data 中
    for filename_base in filenames:
        result_dict = buildDemo(filename_base)
        item_texture_data["texture_data"]["{}.egg".format(filename_base)] = (result_dict)  # 将处理结果追加到 texture_data

    # 保存处理后的数据回 item_texture.json 文件
    try:
        with open(item_texture_json_path, 'w', encoding='utf-8') as f:
            json.dump(item_texture_data, f, indent=4, ensure_ascii=False)
        print(f"成功更新item_texture.json到 {item_texture_json_path}")
    except Exception as e:
        print(f"保存到 {item_texture_json_path} 时发生错误: {e}")

    except Exception as e:
        print(f"发生错误: {e}")

def copyFiles(src_dir, dest_dir):
    # 遍历源路径中的文件并复制到目标路径
    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_dir, filename)

        # 确保是文件而非目录
        if os.path.isfile(src_file):
            try:
                shutil.copy(src_file, dest_file)  # 复制文件
            except Exception as e:
                print(f"复制文件 {filename} 时发生错误: {e}")

# 调整terrain_texture.json文件(方块图集)
def buildTerrainTextureJson(terrainTexturePath, directory):

    def buildDemo(filename_base):
        # 示例生成的字典内容
        return {
            "textures": "textures/items/egg/{}".format(filename_base)
        }

    # 读取路径1中的 terrain_texture.json 文件
    terrain_texture_json_path = os.path.join(terrainTexturePath, "terrain_texture.json")
    try:
        with open(terrain_texture_json_path, 'r', encoding='utf-8') as f:
            terrain_texture_data = json.load(f)
        print(f"成功读取 {terrain_texture_json_path}")
    except Exception as e:
        print(f"读取 {terrain_texture_json_path} 时发生错误: {e}")
        return

    # 获取路径2中的所有文件名，去掉扩展名
    filenames = [os.path.splitext(f)[0] for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    print(f"从目标路径中获取到 {len(filenames)} 个文件：{filenames}")

    # 调用 ABC 方法处理每个文件名，并将结果保存到 blocks_data 中
    for filename_base in filenames:
        result_dict = buildDemo(filename_base)
        terrain_texture_data["texture_data"]["{}:{}".format(config["name"], filename_base).replace(config["suffix_entity"], config["suffix_block"])] = (result_dict)  # 将处理结果追加到 texture_data

    # 保存处理后的数据回 item_texture.json 文件
    try:
        with open(terrain_texture_json_path, 'w', encoding='utf-8') as f:
            json.dump(terrain_texture_data, f, indent=4, ensure_ascii=False)
        print(f"成功更新terrain_texture.json到 {terrain_texture_json_path}")
    except Exception as e:
        print(f"保存到 {terrain_texture_json_patZh} 时发生错误: {e}")

    except Exception as e:
        print(f"发生错误: {e}")

# 计算整个模型的包围盒
def calculate_bounding_box(model_data):
    min_bound = [float('inf')] * 3  # 初始化为正无穷
    max_bound = [float('-inf')] * 3  # 初始化为负无穷

    # 遍历所有 bone 和 cube
    for geometry in model_data['minecraft:geometry']:
        for bone in geometry['bones']:
            for cube in bone['cubes']:
                origin = cube['origin']
                origin[0]  # 块复位
                origin[2]  # 块复位
                size = cube['size']

                # 计算单个 cube 的最小和最大坐标
                def calculate_cube_bounds(origin, size):
                    # origin 是 [x, y, z], size 是 [width, height, depth]
                    min_point = [origin[i] for i in range(3)]
                    max_point = [origin[i] + size[i] for i in range(3)]
                    return min_point, max_point
                cube_min, cube_max = calculate_cube_bounds(origin, size)

                # 更新全局最小坐标和最大坐标
                for i in range(3):
                    min_bound[i] = min(min_bound[i], cube_min[i])
                    max_bound[i] = max(max_bound[i], cube_max[i])

    minBox = [-max_bound[0] * 0.0625, min_bound[1] * 0.0625, min_bound[2] * 0.0625]
    maxBox = [-min_bound[0] * 0.0625, max_bound[1] * 0.0625, max_bound[2] * 0.0625]
    for i in range(0, 3):
        if minBox[i] < -1:
            minBox[i] = -1.0
        if minBox[i] > 2:
            minBox[i] = 2.0
        if maxBox[i] < -1:
            maxBox[i] = -1.0
        if maxBox[i] > 2:
            maxBox[i] = 2.0
    return minBox, maxBox

# 批量修改包围盒
def changeNeteaseBlock(src_dir, dest_dir):
    # 遍历路径1中的所有文件
    for filename in os.listdir(src_dir):
        # 检查文件是否为 JSON 文件
        if filename.endswith('.json'):
            # 获取文件名的非拓展部分
            base_filename = os.path.splitext(filename)[0].replace(config["suffix_entity"] + ".geo", config["suffix_block"])
            # 获取文件的完整路径
            file_path = os.path.join(src_dir, filename)

            def load_json(file_path):
                with open(file_path, 'r') as file:
                    return json.load(file)

            model_data = load_json(file_path)
            # 计算包围盒
            min_bound, max_bound = calculate_bounding_box(model_data)

            # 在路径2中寻找同名的 JSON 文件
            target_file_path = os.path.join(dest_dir, f"{base_filename}.json")

            # 如果目标文件存在
            if os.path.exists(target_file_path):
                # 读取路径2中的 JSON 文件
                with open(target_file_path, 'r') as file:
                    target_data = json.load(file)

                # 修改 target_data 中 'ggg' 键的值为 111
                if 'minecraft:block' in target_data:
                    target_data["minecraft:block"]["components"]["netease:aabb"]["clip"]["max"] = max_bound
                    target_data["minecraft:block"]["components"]["netease:aabb"]["collision"]["max"] = max_bound
                    target_data["minecraft:block"]["components"]["netease:aabb"]["clip"]["min"] = min_bound
                    target_data["minecraft:block"]["components"]["netease:aabb"]["collision"]["min"] = min_bound

                # 将修改后的数据保存回原文件
                with open(target_file_path, 'w') as file:
                    json.dump(target_data, file, indent=4)

                print(f"包围盒调整完成: {target_file_path}")
            else:
                print(f"包围盒调整失败: {base_filename}.json")

if __name__ == "__main__":

    # 目标texture，运行后将自动对该路径下的全部贴图进行规范化
    input_texture_path = r"D:\测试目录\基岩版贴图"
    # 目标geo，运行后将自动对该路径下的全部贴图进行规范化
    input_geo_path = r"D:\测试目录\基岩版模型"
    # 生成资源目录
    build_Path = r"D:\测试目录"

    config = {
        "subTxtList": ["_entity", "drink_", "_block"],   # 批量删减指定路径下文件名称中的某字串
        "name": "easecation", # ide前缀(easecation:air)
        "prefix": "drink_", # 命名前缀(区分模型类型用)
        "suffix_entity": "_entity", # 命名后缀（实体，不建议改动）
        "suffix_block": "_block",  # 命名后缀（方块，不建议改动）
        "directory": "drinkBlock"   # 次级目录名，表示本次生成的各种资源放在什么那个目录下

    }
    # 0.修正目录(务必执行)
    PackageBuilder.buildDirectories(build_Path, config['directory'])

    # 1.对目标texture目录下的全部模型贴图进行规范化命名(非必选)
    subNameByPath(input_texture_path, config['subTxtList'])
    renameAddByPath(input_texture_path, config['prefix'], config['suffix_entity'], "tex")

    # 2.对目标geo目录下的全部模型进行规范化命名(非必选)
    subNameByPath(input_geo_path, config['subTxtList'])
    renameAddByPath(input_geo_path, config['prefix'], config['suffix_entity'], "geo")

    # 3.修改geo文件中的模型名称
    modifyGeoIdentifier(input_geo_path)

    # 4.生成行为包entitys
    buildBehaviorEntityByDirectory(input_texture_path, build_Path + "\{}\{}\{}".format("behavior_pack", "entities", config["directory"]))

    # 5.生成行为包netease_blocks
    buildBehaviorBlockByDirectory(input_texture_path, build_Path + "\{}\{}".format("behavior_pack", "netease_blocks"))

    # 6.生成资源包entity
    buildResourceBlockByDirectory(input_texture_path, build_Path + "\{}\{}\{}".format("resource_pack", "entity", config["directory"]), config["directory"])

    # 7.调整blocks.json文件(方块定义)
    buildBlocksJson(build_Path + "\{}".format("resource_pack"), input_texture_path)

    # 8.调整item_texture.json文件(实体怪物蛋)
    buildItemTextureJson(build_Path + "\{}\{}".format("resource_pack", "textures"), input_texture_path)

    # 9.调整terrain_texture.json文件(方块图集)
    buildTerrainTextureJson(build_Path + "\{}\{}".format("resource_pack", "textures"), input_texture_path)

    # 10.复制贴图与模型到目标路径
    copyFiles(input_texture_path, (build_Path + "\{}\{}\{}\{}".format("resource_pack", "textures", "entity", config["directory"])))
    copyFiles(input_geo_path, (build_Path + "\{}\{}\{}\{}".format("resource_pack", "models", "entity", config["directory"])))

    # 11.调整neteaseBlock包围盒
    changeNeteaseBlock(
        build_Path+ "\{}\{}\{}\{}".format("resource_pack", "models", "entity", config['directory']),
        build_Path + "\{}\{}".format("behavior_pack", "netease_blocks"))
    print("一键生成结束！！！")