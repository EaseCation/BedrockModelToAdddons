# -*- coding: utf-8 -*-
import json
import shutil
import os
import copy
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from Util.PackageBuilder import buildDirectories
from Presets.behaviorPresets import entityDemo, blockDemo
from threading import Thread


class ResourceBuilderGUI:
    def __init__(self, master):
        self.master = master
        self.builder = None
        self.config = {}
        self.setup_ui()

    def setup_ui(self):
        """初始化用户界面"""
        self.master.title("资源包生成工具 v1.0")
        self.master.geometry("800x600")

        # 配置面板
        config_frame = ttk.LabelFrame(self.master, text="配置参数")
        config_frame.pack(pady=10, padx=10, fill=tk.X)

        # 路径选择
        self.create_path_selector(config_frame, "贴图路径:", "input_texture")
        self.create_path_selector(config_frame, "模型路径:", "input_geo")
        self.create_path_selector(config_frame, "构建路径:", "build_path")

        # 配置参数输入
        params = [
            ("名称前缀(自行决定):", "prefix", "drinks_"),
            ("实体后缀(建议默认):", "suffix_entity", "_entity"),
            ("方块后缀(建议默认):", "suffix_block", "_block"),
            ("命名空间(自行决定):", "name", "ecx"),
            ("子目录名(自行决定):", "directory", "drinkBlock")
        ]
        for label, key, default in params:
            self.create_config_input(config_frame, label, key, default)

        # 操作按钮
        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="开始生成", command=self.start_build).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)

        # 日志输出
        self.log_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD)
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def create_path_selector(self, parent, label, key):
        """创建路径选择组件"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        ttk.Label(frame, text=label, width=10).pack(side=tk.LEFT)
        entry = ttk.Entry(frame, width=50)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(frame, text="浏览...", command=lambda: self.select_path(entry)).pack(side=tk.LEFT)

        setattr(self, f"{key}_entry", entry)

    def create_config_input(self, parent, label, key, default):
        """创建配置参数输入组件"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
        entry = ttk.Entry(frame)
        entry.insert(0, default)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        setattr(self, f"{key}_entry", entry)

    def select_path(self, entry):
        """处理路径选择"""
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def log(self, message):
        """日志输出"""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def clear_log(self):
        """清空日志"""
        self.log_area.delete(1.0, tk.END)

    def get_config(self):
        """获取配置参数"""
        return {
            "subTxtList": ["_entity", "drink_", "drinks_", "_block"],
            "name": self.name_entry.get(),
            "prefix": self.prefix_entry.get(),
            "suffix_entity": self.suffix_entity_entry.get(),
            "suffix_block": self.suffix_block_entry.get(),
            "directory": self.directory_entry.get()
        }

    def start_build(self):
        """启动构建过程"""
        self.config = self.get_config()
        input_texture = self.input_texture_entry.get()
        input_geo = self.input_geo_entry.get()
        build_path = self.build_path_entry.get()

        if not all([input_texture, input_geo, build_path]):
            self.log("错误：请先设置所有路径！")
            return

        # 在后台线程中执行构建
        Thread(target=self.run_build_process, args=(build_path, input_texture, input_geo)).start()

    def run_build_process(self, build_path, input_texture, input_geo):
        """执行构建流程"""
        try:
            self.builder = ResourceBuilder(self.config)

            # 0. 创建目录
            self.log("\n=== 正在创建目录结构 ===")
            buildDirectories(build_path, self.config['directory'])

            # 1-2. 文件名处理
            self.process_naming(input_texture, "tex")
            self.process_naming(input_geo, "geo")

            # 3. 修改geo标识符
            self.log("\n=== 正在更新模型标识 ===")
            self.builder.modify_geo_identifier(input_geo)

            # 4-6. 生成行为包和资源包
            self.generate_packages(build_path, input_texture)

            # 7-9. 更新JSON文件
            self.update_json_files(build_path, input_texture)

            # 10. 复制文件
            self.copy_resources(build_path, input_texture, input_geo)

            # 11. 调整包围盒
            self.adjust_bounding_boxes(build_path)

            self.log("\n=== 全部操作已完成！ ===")
        except Exception as e:
            self.log(f"\n发生严重错误: {str(e)}")

    def process_naming(self, path, file_type):
        """处理命名操作"""
        self.log(f"\n=== 正在处理 {os.path.basename(path)} 的命名 ===")
        self.builder.sub_name_by_path(path, self.config['subTxtList'])
        self.builder.rename_add_by_path(
            path,
            self.config['prefix'],
            self.config['suffix_entity'],
            file_type
        )

    def generate_packages(self, build_path, input_texture):
        """生成各类资源包"""
        self.log("\n=== 正在生成行为包和资源包 ===")
        paths = {
            "behavior_entity": os.path.join(build_path, self.builder.BEHAVIOR_PACK, "entities",
                                            self.config["directory"]),
            "behavior_block": os.path.join(build_path, self.builder.BEHAVIOR_PACK, "netease_blocks"),
            "resource_entity": os.path.join(build_path, self.builder.RESOURCE_PACK, self.builder.ENTITY,
                                            self.config["directory"])
        }

        self.builder.build_behavior_entity_by_directory(input_texture, paths["behavior_entity"])
        self.builder.build_behavior_block_by_directory(input_texture, paths["behavior_block"])
        self.builder.build_resource_block_by_directory(input_texture, paths["resource_entity"],
                                                       self.config["directory"])

    def update_json_files(self, build_path, input_texture):
        """更新JSON配置文件"""
        self.log("\n=== 正在更新配置文件 ===")
        json_paths = {
            "blocks_json": os.path.join(build_path, self.builder.RESOURCE_PACK),
            "item_texture": os.path.join(build_path, self.builder.RESOURCE_PACK, self.builder.TEXTURES),
            "terrain_texture": os.path.join(build_path, self.builder.RESOURCE_PACK, self.builder.TEXTURES)
        }

        # 更新blocks.json
        self.builder.build_json_blocks(
            os.path.join(json_paths["blocks_json"],"blocks.json"),
            input_texture,
            lambda filename_base: {
                    "client_entity": {
                        "hand_model_use_client_entity": True,
                        "identifier": f"{self.config['name']}:{filename_base}",
                        "block_icon": f"{self.config['name']}:{filename_base}".replace(
                            self.config["suffix_entity"], self.config["suffix_block"])
                    },
                    "sound": "metal"
                },
            json_key=self.config["name"]
        )

        # 更新 item_texture.json
        self.builder.build_json_item_texture(
            os.path.join(json_paths["item_texture"],"item_texture.json"),
            input_texture,
            lambda filename_base: {
                "textures": f"textures/items/egg/{filename_base}"
                }

        )

        # 更新 terrain_texture.json
        self.builder.build_json_terrain_texture(
            os.path.join(json_paths["terrain_texture"],"terrain_texture.json"),
            input_texture,
            lambda filename_base: {
                    "textures": f"textures/items/egg/{filename_base}"
                },
            json_key=self.config["name"]
        )

    def copy_resources(self, build_path, input_texture, input_geo):
        """复制资源文件"""
        self.log("\n=== 正在复制资源文件 ===")
        self.builder.copy_files(
            input_texture,
            os.path.join(build_path, self.builder.RESOURCE_PACK, self.builder.TEXTURES,
                         self.builder.ENTITY, self.config["directory"])
        )
        self.builder.copy_files(
            input_geo,
            os.path.join(build_path, self.builder.RESOURCE_PACK, self.builder.MODELS,
                         self.builder.ENTITY, self.config["directory"])
        )

    def adjust_bounding_boxes(self, build_path):
        """调整包围盒"""
        self.log("\n=== 正在调整包围盒 ===")
        geo_model_path = os.path.join(
            build_path, self.builder.RESOURCE_PACK, self.builder.MODELS,
            self.builder.ENTITY, self.config['directory']
        )
        netease_block_path = os.path.join(build_path, self.builder.BEHAVIOR_PACK, "netease_blocks")
        self.builder.change_netease_block(geo_model_path, netease_block_path)


class ResourceBuilder:
        def __init__(self, config):
            self.config = config
            self.BEHAVIOR_PACK = "behavior_pack"
            self.RESOURCE_PACK = "resource_pack"
            self.TEXTURES = "textures"
            self.MODELS = "models"
            self.ENTITY = "entity"

        def sub_name_by_path(self, path, txt_list):
            """
            批量删除文件名中包含的子串

            参数:
                path (str): 目标文件夹路径
                txt_list (list): 需要删除的子串列表
            """
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if os.path.isdir(file_path):
                    continue

                new_filename = filename
                for txt in txt_list:
                    if txt in new_filename:
                        new_filename = new_filename.replace(txt, '')

                if new_filename != filename:
                    new_file_path = os.path.join(path, new_filename)
                    if not os.path.exists(new_file_path):
                        os.rename(file_path, new_file_path)

        def rename_add_by_path(self, path, prefix, suffix, directory_type):
            """
            批量修改文件名

            参数:
                path (str): 目标文件夹路径
                prefix (str): 文件名前缀
                suffix (str): 文件名后缀
                directory_type (str): 目录类型（geo 或 tex）
            """
            try:
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)
                    if os.path.isfile(full_path):
                        file_name, file_extension = os.path.splitext(entry)
                        file_name = file_name.replace(".geo", "")
                        new_filename = f"{prefix}{file_name}{suffix}.geo{file_extension}" if directory_type == "geo" else f"{prefix}{file_name}{suffix}{file_extension}"
                        new_path = os.path.join(path, new_filename)
                        os.rename(full_path, new_path)
                        print(f"规范化命名: {entry} -> {new_filename}")
            except Exception as e:
                print(f"发生错误: {e}")

        def modify_geo_identifier(self, path):
            """
            批量修改geo中的identifier

            参数:
                path (str): 目标文件夹路径
            """

            def update_identifier(data, filename_base):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == "identifier" and isinstance(value, str):
                            data[key] = f"geometry.{filename_base}"
                        else:
                            update_identifier(value, filename_base)
                elif isinstance(data, list):
                    for item in data:
                        update_identifier(item, filename_base)
                return data

            try:
                for filename in os.listdir(path):
                    if filename.endswith(".json"):
                        full_path = os.path.join(path, filename)
                        filename_base = os.path.splitext(filename)[0].replace(".geo", "")
                        with open(full_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        updated_data = update_identifier(data, filename_base)
                        with open(full_path, 'w', encoding='utf-8') as f:
                            json.dump(updated_data, f, indent=4, ensure_ascii=False)
                        print(f"已修正Geometry名称: {filename}")
            except Exception as e:
                print(f"发生错误: {e}")

        def build_behavior_entity_by_directory(self, input_directory, output_directory):
            """
            批量生成生物行为包

            参数:
                input_directory (str): 输入目录路径
                output_directory (str): 输出目录路径
            """

            def build_demo(filename_base):
                behavior_data = copy.deepcopy(entityDemo)
                behavior_data["minecraft:entity"]["description"]["identifier"] = "{}:{}".format(self.config["name"],
                                                                                                filename_base)
                return behavior_data

            try:
                for filename in os.listdir(input_directory):
                    filename_base = os.path.splitext(filename)[0]
                    result_dict = build_demo(filename_base)
                    output_file_path = os.path.join(output_directory, f"{filename_base}.json")
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        json.dump(result_dict, f, indent=4, ensure_ascii=False)
                    print(f"已生成行为数据{filename_base}.json并保存到: {output_file_path}")
            except Exception as e:
                print(f"发生错误: {e}")

        def build_behavior_block_by_directory(self, input_directory, output_directory):
            """
            批量生成方块行为包

            参数:
                input_directory (str): 输入目录路径
                output_directory (str): 输出目录路径
            """

            def generate_block_behavior(filename_base):
                behavior = copy.deepcopy(blockDemo)
                behavior["minecraft:block"]["description"]["identifier"] = "{}:{}".format(self.config["name"],
                                                                                          filename_base)
                return behavior

            os.makedirs(output_directory, exist_ok=True)
            try:
                for filename in os.listdir(input_directory):
                    filename_base = os.path.splitext(filename)[0].replace(self.config["suffix_entity"],
                                                                          self.config["suffix_block"])
                    behavior_dict = generate_block_behavior(filename_base)
                    output_file_path = os.path.join(output_directory, f"{filename_base}.json")
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        json.dump(behavior_dict, output_file, indent=4, ensure_ascii=False)
                    print(f"已生成netease_blocks输出到: {output_file_path}")
            except Exception as e:
                print(f"发生错误: {e}")

        def build_resource_block_by_directory(self, input_directory, output_directory, path):
            """
            批量生成生物资源包

            参数:
                input_directory (str): 输入目录路径
                output_directory (str): 输出目录路径
                path (str): 资源路径
            """

            def build_behavior(filename_base):
                return {
                    "format_version": "1.10.0",
                    "minecraft:client_entity": {
                        "description": {
                            "geometry": {"default": f"geometry.{filename_base}"},
                            "identifier": f"{self.config['name']}:{filename_base}",
                            "materials": {"default": "entity_alphatest"},
                            "render_controllers": ["controller.render.default"],
                            "spawn_egg": {
                                "texture": f"{filename_base}.egg",
                                "texture_index": 0
                            },
                            "textures": {
                                "default": f"textures/entity/{path}/{filename_base}"
                            }
                        }
                    }
                }

            os.makedirs(output_directory, exist_ok=True)
            try:
                for filename in os.listdir(input_directory):
                    filename_base = os.path.splitext(filename)[0]
                    result_dict = build_behavior(filename_base)
                    output_file_path = os.path.join(output_directory, f"{filename_base}.json")
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        json.dump(result_dict, f, indent=4, ensure_ascii=False)
                    print(f"已根据: {filename} -> 生成资源包Entity输出到: {output_file_path}")
            except Exception as e:
                print(f"发生错误: {e}")

        def build_json_blocks(self, json_path, directory, build_demo, json_key=None):
            """
            通用blocks.json文件生成函数

            参数:
                json_path (str): JSON文件路径
                directory (str): 目标目录路径
                build_demo (function): 生成字典的函数
                json_key (str): JSON文件中需要更新的键
            """
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                print(f"成功读取 {json_path}")
            except Exception as e:
                print(f"读取 {json_path} 时发生错误: {e}")
                return

            filenames = [os.path.splitext(f)[0] for f in os.listdir(directory)
                         if os.path.isfile(os.path.join(directory, f))]
            print(f"从目标路径中获取到 {len(filenames)} 个文件：{filenames}")

            for filename_base in filenames:
                # 生成原始数据字典
                result_dict = build_demo(filename_base)

                # 构造新的完整键名（带命名空间和后缀替换）
                if json_key:
                    formatted_key = f"{json_key}:{filename_base.replace(self.config['suffix_entity'], self.config['suffix_block'])}"
                else:
                    formatted_key = f"{filename_base.replace(self.config['suffix_entity'], self.config['suffix_block'])}"
                # 直接写入顶层字典
                json_data[formatted_key] = result_dict

            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)
                print(f"成功更新JSON文件到 {json_path}")
            except Exception as e:
                print(f"保存到 {json_path} 时发生错误: {e}")

        def build_json_item_texture(self, json_path, directory, build_demo, json_key=None):
            """
            通用item_texture.json文件生成函数

            参数:
                json_path (str): JSON文件路径
                directory (str): 目标目录路径
                build_demo (function): 生成字典的函数
                json_key (str): JSON文件中需要更新的键
            """
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                print(f"成功读取 {json_path}")
            except Exception as e:
                print(f"读取 {json_path} 时发生错误: {e}")
                return

            filenames = [os.path.splitext(f)[0] for f in os.listdir(directory)
                         if os.path.isfile(os.path.join(directory, f))]
            print(f"从目标路径中获取到 {len(filenames)} 个文件：{filenames}")

            # 确保 "texture_data" 键存在
            if "texture_data" not in json_data:
                json_data["texture_data"] = {}

            for filename_base in filenames:
                # 生成原始数据字典
                result_dict = build_demo(filename_base)

                # 构造新的完整键名（带命名空间和后缀替换）
                if json_key:
                    formatted_key = f"{json_key}:{filename_base}.egg"
                else:
                    formatted_key = f"{filename_base}.egg"

                # 将生成的字典内容写入到 "texture_data" 中
                json_data["texture_data"][formatted_key] = result_dict

            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)
                print(f"成功更新JSON文件到 {json_path}")
            except Exception as e:
                print(f"保存到 {json_path} 时发生错误: {e}")

        def build_json_terrain_texture(self, json_path, directory, build_demo, json_key=None):
            """
            通用terrain_texture.json文件生成函数

            参数:
                json_path (str): JSON文件路径
                directory (str): 目标目录路径
                build_demo (function): 生成字典的函数
                json_key (str): JSON文件中需要更新的键
            """
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                print(f"成功读取 {json_path}")
            except Exception as e:
                print(f"读取 {json_path} 时发生错误: {e}")
                return

            filenames = [os.path.splitext(f)[0] for f in os.listdir(directory)
                         if os.path.isfile(os.path.join(directory, f))]
            print(f"从目标路径中获取到 {len(filenames)} 个文件：{filenames}")

            # 确保 "texture_data" 键存在
            if "texture_data" not in json_data:
                json_data["texture_data"] = {}

            for filename_base in filenames:
                # 生成原始数据字典
                result_dict = build_demo(filename_base)

                # 构造新的完整键名（带命名空间和后缀替换）
                if json_key:
                    formatted_key = f"{json_key}:{filename_base.replace(self.config['suffix_entity'], self.config['suffix_block'])}"
                else:
                    formatted_key = f"{filename_base.replace(self.config['suffix_entity'], self.config['suffix_block'])}"

                # 将生成的字典内容添加到 "texture_data" 中
                json_data["texture_data"][formatted_key] = result_dict

            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)
                print(f"成功更新JSON文件到 {json_path}")
            except Exception as e:
                print(f"保存到 {json_path} 时发生错误: {e}")

        def copy_files(self, src_dir, dest_dir):
            """
            复制文件

            参数:
                src_dir (str): 源目录路径
                dest_dir (str): 目标目录路径
            """
            for filename in os.listdir(src_dir):
                src_file = os.path.join(src_dir, filename)
                dest_file = os.path.join(dest_dir, filename)
                if os.path.isfile(src_file):
                    try:
                        shutil.copy(src_file, dest_file)
                    except Exception as e:
                        print(f"复制文件 {filename} 时发生错误: {e}")

        def calculate_bounding_box(self, model_data):
            """
            计算模型的包围盒

            参数:
                model_data (dict): 模型数据

            返回:
                tuple: 最小和最大包围盒坐标
            """
            min_bound = [float('inf')] * 3
            max_bound = [float('-inf')] * 3

            for geometry in model_data['minecraft:geometry']:
                for bone in geometry['bones']:
                    for cube in bone['cubes']:
                        origin = cube['origin']
                        size = cube['size']
                        cube_min = [origin[i] for i in range(3)]
                        cube_max = [origin[i] + size[i] for i in range(3)]
                        for i in range(3):
                            min_bound[i] = min(min_bound[i], cube_min[i])
                            max_bound[i] = max(max_bound[i], cube_max[i])

            minBox = [-max_bound[0] * 0.0625, min_bound[1] * 0.0625, min_bound[2] * 0.0625]
            maxBox = [-min_bound[0] * 0.0625, max_bound[1] * 0.0625, max_bound[2] * 0.0625]
            for i in range(3):
                minBox[i] = max(minBox[i], -1.0)
                minBox[i] = min(minBox[i], 2.0)
                maxBox[i] = max(maxBox[i], -1.0)
                maxBox[i] = min(maxBox[i], 2.0)
            return minBox, maxBox

        def change_netease_block(self, src_dir, dest_dir):
            """
            批量修改包围盒

            参数:
                src_dir (str): 源目录路径
                dest_dir (str): 目标目录路径
            """
            for filename in os.listdir(src_dir):
                if filename.endswith('.json'):
                    base_filename = os.path.splitext(filename)[0].replace(self.config["suffix_entity"] + ".geo",
                                                                          self.config["suffix_block"])
                    file_path = os.path.join(src_dir, filename)

                    with open(file_path, 'r') as file:
                        model_data = json.load(file)
                    min_bound, max_bound = self.calculate_bounding_box(model_data)

                    target_file_path = os.path.join(dest_dir, f"{base_filename}.json")
                    if os.path.exists(target_file_path):
                        with open(target_file_path, 'r') as file:
                            target_data = json.load(file)

                        if 'minecraft:block' in target_data:
                            target_data["minecraft:block"]["components"]["netease:aabb"]["clip"]["max"] = max_bound
                            target_data["minecraft:block"]["components"]["netease:aabb"]["collision"]["max"] = max_bound
                            target_data["minecraft:block"]["components"]["netease:aabb"]["clip"]["min"] = min_bound
                            target_data["minecraft:block"]["components"]["netease:aabb"]["collision"]["min"] = min_bound

                        with open(target_file_path, 'w') as file:
                            json.dump(target_data, file, indent=4)
                        print(f"包围盒调整完成: {target_file_path}")
                    else:
                        print(f"包围盒调整失败: {base_filename}.json")

if __name__ == "__main__":
    root = tk.Tk()
    app = ResourceBuilderGUI(root)
    root.mainloop()