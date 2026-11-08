D1 = 4  # 零件1的购买单价
D2 = 18  # 零件2的购买单价
Q1 = 2 # 零件1的检测成本
Q2 = 3  # 零件2的检测成本
Q3 = 3  # 成品的检测成本
P1 = 0.055 # 零件1的次品率
P2 = 0.045 # 零件2的次品率
P3 = 0.05  # 成品的次品率
Z = 6  # 装配成本
H = 10 # 调换损失费用
C = 40  # 拆解费用
S = 56  # 市场售价
N = 1000  # 初始零件购买数
MAX_ITERATIONS = 1  # 最多迭代次数
def calculate_path_cost(strategy, product_check, replace_untested, disassemble_tested, n_parts, iteration_count):
    if n_parts <= 0 or iteration_count >= MAX_ITERATIONS:
        return 0
    total_cost = (D1 + D2) * n_parts
    # 第一层：检测零配件的成本
    if strategy in ['check_1', 'check_2', 'check_both']:
        if strategy == 'check_1':
            total_cost += Q1 * n_parts
            Ng = (1 - P1) * n_parts
        elif strategy == 'check_2':
            total_cost += Q2 * n_parts
            Ng = (1 - P2) * n_parts
        else:  # 'check_both'
            total_cost += (Q1 + Q2) * n_parts
            Ng = (1 - P1) * (1 - P2) * n_parts
    else:
        Ng = n_parts  # No check, assume all parts pass
    total_cost += Z * Ng
    # 成品检测与市场结果
    if product_check:
        total_cost += Q3 * Ng
        non_defective = Ng * (1 - P3)  # 合格成品数量
        defective = Ng * P3  # 不合格成品数量
        total_cost -= S * non_defective  # 合格成品售卖收入减少
        if disassemble_tested:
            # 如果拆解不合格成品，减去其零件成本
            total_cost += C * defective  # 拆解成本
            total_cost -= (D1 + D2) * defective * 2  # 减去回收的零件成本，每个成品有两个零件
    else:
        # 不检测的成品直接进入市场
        total_cost -= S * Ng
        if replace_untested:  # 市场反馈导致的调换
            total_cost += H * Ng * P3  # 调换不合格成品的成本
            if disassemble_tested:  # 调换后对不合格成品进行拆解
                total_cost += C * Ng * P3  # 拆解费用
                total_cost -= (D1 + D2) * Ng * P3 * 2  # 减去拆解后回收的零件成本
    return total_cost
# 生成所有可能的路径
paths = []
for strategy in ['check_1', 'check_2', 'check_both', 'no_check']:
    for product_check in [True, False]:
        for replace_untested in [True, False]:
            for disassemble_tested in [True, False]:
                cost = calculate_path_cost(strategy, product_check, replace_untested, disassemble_tested, N, 0)
                paths.append(
                    (strategy, product_check, replace_untested, disassemble_tested, cost))
# 找到总损耗最小的路径
best_path = min(paths, key=lambda x: x[-1])
# 输出最小消耗的路径
print("最小消耗的路径:")
print(f"零件检测: {best_path[0]}, 成品检测: {best_path[1]}")
if not best_path[1]:  # 如果没有进行成品检测
    if best_path[2]:  # 如果进行了未检测成品调换
        print(f"未检测成品调换: {best_path[2]}")
    if best_path[2] and best_path[3]:  # 如果进行了调换后的拆解
        print(f"调换后的拆解: {best_path[3]}")
if best_path[1]:  # 如果进行了成品检测
    if best_path[3]:  # 如果进行了检测不合格成品拆解
        print(f"检测不合格成品拆解: {best_path[3]}")
print(f"总损耗: {best_path[-1]}")
