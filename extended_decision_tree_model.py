import itertools
import random
 
# 基本参数
num_parts_purchased = 1000
prices = [2, 8, 12, 2, 8, 12, 8, 12]  # 零件单价
detection_costs = [1, 1, 2, 1, 1, 2, 1, 2]  # 零件检测成本
subassembly_detection_costs = [4, 4, 4]  # 半成品检测成本
product_detection_cost = 6  # 成品检测成本
assembly_costs = [8, 8, 8]  # 半成品装配成本
product_assembly_cost = 8  # 成品装配成本
disassembly_costs = [6, 6, 6, 10]  # 半成品和成品拆解成本
market_price = 200  # 成品市场售价
replacement_loss = 40  # 成品调换损失
 
defect_rates = [0.11,0.09,0.1,0.095,0.115,0.105,0.10,0.085]   # 零件次品率
subassembly_defect_rates = [0.12,0.095,0.105]  # 半成品次品率
product_defect_rate = 0.10  # 成品次品率
 
 
# 根节点：确定零件检测情况
def root_node():
    configurations = list(itertools.product([True, False], repeat=8))  # 每个零件是否检测
    return configurations
 
 
# 层2：计算根节点的损耗并判断零件是否合格
def calculate_root_loss(config):
    total_cost = 0
    parts_quality = [None] * 8  # 用 None 表示不确定是否合格
 
    for i in range(8):
        if config[i]:  # 如果检测
            total_cost += detection_costs[i] * num_parts_purchased  # 增加检测成本
            is_qualified = random.random() >= defect_rates[i]  # 判断合格性
            parts_quality[i] = is_qualified
        else:
            parts_quality[i] = None  # 未检测，状态未知
 
    return parts_quality, total_cost
 
 
# 基于次品率决定需要拆解的数量，并返回相应的拆解损耗
def calculate_disassembly_loss(total_units, defect_rate, disassembly_cost):
    num_to_disassemble = int(defect_rate * total_units)  # 根据次品率确定需要拆解的数量
    return num_to_disassemble * disassembly_cost  # 返回拆解的总损耗
 
 
# 半成品装配和检测
def assemble_subassemblies(parts_quality, subassembly_detection_config):
    subassemblies_quality = [None] * 3  # 半成品合格性未知
    total_cost = 0
    subassembly_info = []  # 存储拆解信息
 
    part_groups = [[0, 1, 2], [3, 4, 5], [6, 7]]  # 每组对应半成品
    for i, group in enumerate(part_groups):
        if None in [parts_quality[idx] for idx in group]:  # 如果零件状态不确定
            subassemblies_quality[i] = None
        elif all(parts_quality[idx] for idx in group):  # 全部零件明确合格
            total_cost += assembly_costs[i] * num_parts_purchased  # 装配成本
            if subassembly_detection_config[i]:  # 如果选择检测半成品
                total_cost += subassembly_detection_costs[i] * num_parts_purchased  # 半成品检测成本
                is_qualified = random.random() >= subassembly_defect_rates[i]  # 判断合格性
                subassemblies_quality[i] = is_qualified
            else:
                subassemblies_quality[i] = None  # 未知状态
        else:
            subassemblies_quality[i] = False
            total_cost += disassembly_costs[i] * num_parts_purchased  # 半成品拆解损耗
            total_cost -= sum(prices[idx] * num_parts_purchased for idx in group)  # 扣除零配件的购买成本
            subassembly_info.append(f"不合格半成品{i + 1} 拆解")  # 添加半成品拆解信息
 
    return subassemblies_quality, total_cost, subassembly_info
 
 
# 成品装配和检测
def assemble_product(parts_quality, subassembly_detection_config, product_detection):
    total_cost = 0
    subassemblies_quality, subassembly_cost, subassembly_info = assemble_subassemblies(parts_quality,
                                                                                       subassembly_detection_config)
    total_cost += subassembly_cost + product_assembly_cost * num_parts_purchased
    product_info = []
 
    if product_detection:
        total_cost += product_detection_cost * num_parts_purchased
        disassembly_loss = calculate_disassembly_loss(num_parts_purchased, product_defect_rate, disassembly_costs[3])
        product_info.append(f"不合格成品检测后拆解，拆解损耗: {disassembly_loss}")
    else:
        disassembly_loss = calculate_disassembly_loss(num_parts_purchased, product_defect_rate, disassembly_costs[3])
        product_info.append(f"不合格成品未检测拆解，拆解损耗: {disassembly_loss}")
 
    total_cost += disassembly_loss  # 增加成品拆解损耗
 
    # 成品销售收入
    total_cost -= market_price * num_parts_purchased
 
    return total_cost, subassembly_info, product_info
 
 
# 计算路径的总损耗
def calculate_total_loss(config, subassembly_detection_config, product_detection):
    parts_quality, total_cost = calculate_root_loss(config)
 
    # 计算半成品的拆解损耗（基于10%的次品率）
    total_disassembly_loss_subassembly = sum(
        calculate_disassembly_loss(num_parts_purchased, subassembly_defect_rates[i], disassembly_costs[i])
        for i in range(3)
    )
 
    total_cost += total_disassembly_loss_subassembly  # 增加半成品的拆解损耗
    product_cost, subassembly_info, product_info = assemble_product(parts_quality, subassembly_detection_config,
                                                                    product_detection)
    total_cost += product_cost
 
    return total_cost, subassembly_info, product_info
 
 
# 寻找最优路径并记录前10名最小消耗路径
def find_optimal_paths():
    configurations = root_node()
    subassembly_detection_configs = list(itertools.product([True, False], repeat=3))  # 半成品检测的选择
    product_detection_configs = [True, False]  # 成品检测的选择
    results = []
 
    for config in configurations:
        for subassembly_config in subassembly_detection_configs:
            for product_detection in product_detection_configs:
                loss, subassembly_info, product_info = calculate_total_loss(config, subassembly_config,
                                                                            product_detection)
                results.append((config, subassembly_config, product_detection, loss, subassembly_info, product_info))
 
    # 按损耗排序并获取前10个最小消耗的路径
    results.sort(key=lambda x: x[3])
    return results[:10]
 
 
# 打印路径决策信息
def print_top_10_paths():
    top_10_paths = find_optimal_paths()
    for i, (config, subassembly_config, product_detection, loss, subassembly_info, product_info) in enumerate(
            top_10_paths, 1):
        print(f"\n路径 {i}：")
        print("零件检测决策: " + " -> ".join([f"零件{i + 1}检测={d}" for i, d in enumerate(config)]))
        print("半成品检测决策: " + " -> ".join([f"半成品{i + 1}检测={d}" for i, d in enumerate(subassembly_config)]))
        print(f"成品检测决策: 成品检测={product_detection}")
        print(f"总损耗: {loss}")
        print("半成品拆解信息: ", " -> ".join(subassembly_info))
        print("成品拆解信息: ", " -> ".join(product_info))
 
 
# 运行代码
print_top_10_paths()
