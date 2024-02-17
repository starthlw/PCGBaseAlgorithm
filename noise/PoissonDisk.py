import tkinter as tk
from tkinter import messagebox
import random
import math
import matplotlib.pyplot as plt
import numpy as np


class NoiseEditor:
    def __init__(self, root):
        # 创建输入框和标签
        tk.Label(root, text="宽度").grid(row=0)
        self.width_entry = tk.Entry(root)
        self.width_entry.grid(row=0, column=1)
        self.width_entry.insert(0, '10')

        tk.Label(root, text="高度").grid(row=0, column=2)
        self.height_entry = tk.Entry(root)
        self.height_entry.grid(row=0, column=3)
        self.height_entry.insert(0, '10')

        tk.Label(root, text="半径").grid(row=1)
        self.r_entry = tk.Entry(root)
        self.r_entry.grid(row=1, column=1)
        self.r_entry.insert(0, '1')

        tk.Label(root, text="尝试次数").grid(row=1, column=2)
        self.k_entry = tk.Entry(root)
        self.k_entry.grid(row=1, column=3)
        self.k_entry.insert(0, '30')

        # 创建按钮
        tk.Button(root, text="开始采样", command=self.sample_points).grid(row=2)

    def point_valid(self, pt, pts, r):
        for point in pts:  # 依次判断两点间距
            if np.linalg.norm(np.array(pt)-np.array(point)) < r:
                return False
        return True

    def sample_points(self):
        # 获取用户输入的参数
        try:
            width = float(self.width_entry.get())
            height = float(self.height_entry.get())
            r = float(self.r_entry.get())
            k = int(self.k_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的参数")
            return

        # 初始化
        grid_width = int(width / r)
        grid_height = int(height / r)
        grid = np.zeros((grid_width, grid_height))
        active_list = []

        # 随机选择一个初始点
        x, y = random.uniform(0, width), random.uniform(0, height)
        i, j = int(x / r), int(y / r)
        grid[i][j] = 1
        active_list.append((x, y))

        max_iterations = 1000
        iterations = 0
        plt.figure()
        debug_lines = []

        # 开始采样
        while active_list:
            # 随机选择一个活动点
            x, y = random.choice(active_list)

            # 尝试生成新点
            for _ in range(k):
                # 随机生成一个角度和距离
                theta = random.uniform(0, 2 * math.pi)
                radius = random.uniform(r, 2 * r)
                x0, y0 = x + radius * math.cos(theta), y + radius * math.sin(theta)

                if 0 <= x0 < width and 0 <= y0 < height:
                    i0, j0 = int(x0 / r), int(y0 / r)

                    if grid[i0][j0] == 0 and self.point_valid((x0, y0), active_list, r):
                        grid[i0][j0] = 1
                        active_list.append((x0, y0))
                        debug_lines.append(((x, y), (x0, y0)))
                        break

            iterations += 1
            if iterations == max_iterations:
                break

            # 显示当前点集
            plt.cla()
            plt.xlim(0, width)
            plt.ylim(0, height)
            plt.scatter(*zip(*active_list))
            for point in active_list:
                circle = plt.Circle(point, r / 2, fill=False)
                plt.gca().add_patch(circle)
            for line in debug_lines:
                plt.plot(*zip(*line), 'r-')
            plt.pause(0.01)
        plt.show()


# 创建主窗口
root = tk.Tk()
root.title("泊松盘采样")
NoiseEditor(root)
root.mainloop()