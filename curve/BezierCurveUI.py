import tkinter as tk


class CurveEditor:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=1024, height=768)
        self.canvas.pack()
        self.points = []  # 主控制点
        self.point_ids = []  # 主控制点的ID
        self.handle_points = []  # 权重控制点
        self.handle_point_ids = []  # 权重控制点的ID
        self.selected_point = None
        self.selected_handle = None  # 当前选中的权重控制点

        # 曲线类型选择
        self.curve_type = tk.StringVar(master)
        self.curve_type.set("N-Bezier")  # 默认值
        self.curve_type_options = ["N-Bezier", "MultiplyBezier"]
        self.option_menu = tk.OptionMenu(master, self.curve_type, *self.curve_type_options,
                                         command=self.curve_type_changed)
        self.option_menu.pack()

        self.canvas.bind("<Button-1>", self.add_or_select_point)
        self.canvas.bind("<Button-3>", self.delete_point)
        self.canvas.bind("<B1-Motion>", self.move_point_or_handle)
        self.canvas.bind("<ButtonRelease-1>", self.deselect_point)

        self.points_radius = 8
        self.handle_points_radius = 6

    def curve_type_changed(self, value):
        print(f"Selected curve type: {value}")
        self.update_curve()

    def add_or_select_point(self, event):
        # 检查是否点击了现有的权重控制点
        for i, handle_id in enumerate(self.handle_point_ids):
            x1, y1, x2, y2 = self.canvas.coords(handle_id)
            if x1 < event.x < x2 and y1 < event.y < y2:
                self.selected_handle = i
                return
        # 检查是否点击了现有的主控制点
        for i, point_id in enumerate(self.point_ids):
            x1, y1, x2, y2 = self.canvas.coords(point_id)
            if x1 < event.x < x2 and y1 < event.y < y2:
                self.selected_point = i
                return
        # 添加新的控制点
        self.create_point(event.x, event.y)
        self.draw_handle_lines()

    def create_point(self, x, y):
        # 为新的节点创建控制点
        point_id = self.canvas.create_oval(x - self.points_radius, y - self.points_radius,
                                           x + self.points_radius, y + self.points_radius, fill='red', tags="point")
        self.points.append((x, y))
        self.point_ids.append(point_id)
        # 为新的节点创建两个控制点，一个在左侧，一个在右侧
        # 注意：首尾节点的处理可能需要特殊逻辑
        handle_id_left = self.canvas.create_oval(x - 20 - self.handle_points_radius, y - self.handle_points_radius,
                                                 x - 20 + self.handle_points_radius, y + self.handle_points_radius,
                                                 fill='green', tags="handle")
        handle_id_right = self.canvas.create_oval(x + 20 - self.handle_points_radius, y - self.handle_points_radius,
                                                  x + 20 + self.handle_points_radius, y + self.handle_points_radius,
                                                  fill='green', tags="handle")
        self.handle_points.append((x - 20, y))  # 左侧控制点
        self.handle_points.append((x + 20, y))  # 右侧控制点
        self.handle_point_ids.append(handle_id_left)
        self.handle_point_ids.append(handle_id_right)
        self.update_curve()

    def move_point_or_handle(self, event):
        if self.selected_point is not None:
            # 移动主控制点
            self.canvas.coords(self.point_ids[self.selected_point], event.x - self.points_radius,
                               event.y - self.points_radius, event.x + self.points_radius, event.y + self.points_radius)
            self.points[self.selected_point] = (event.x, event.y)
            # 同时移动关联的权重控制点
            handle_id = self.handle_point_ids[self.selected_point]
            hx, hy = self.handle_points[self.selected_point]
            self.canvas.coords(handle_id, event.x + (hx - event.x) - self.handle_points_radius,
                               event.y + (hy - event.y) - self.handle_points_radius,
                               event.x + (hx - event.x) + self.handle_points_radius,
                               event.y + (hy - event.y) + self.handle_points_radius)
            self.handle_points[self.selected_point] = (event.x + (hx - event.x), event.y + (hy - event.y))
        elif self.selected_handle is not None:
            # 移动权重控制点
            self.canvas.coords(self.handle_point_ids[self.selected_handle], event.x - self.handle_points_radius,
                               event.y - self.handle_points_radius, event.x + self.handle_points_radius,
                               event.y + self.handle_points_radius)
            self.handle_points[self.selected_handle] = (event.x, event.y)
        self.update_curve()

    def delete_point(self, event):
        # 检查是否点击了现有的主控制点，并删除
        for i, point_id in enumerate(self.point_ids):
            x1, y1, x2, y2 = self.canvas.coords(point_id)
            if x1 < event.x < x2 and y1 < event.y < y2:
                self.canvas.delete(point_id)
                # 删除与之关联的两个权重控制点
                handle_id1 = self.handle_point_ids[2 * i]  # 获取第一个权重控制点的ID
                handle_id2 = self.handle_point_ids[2 * i + 1]  # 获取第二个权重控制点的ID
                self.canvas.delete(handle_id1)
                self.canvas.delete(handle_id2)
                # 从列表中移除
                del self.points[i]
                del self.point_ids[i]
                del self.handle_points[2 * i:2 * i + 2]  # 删除两个权重控制点
                del self.handle_point_ids[2 * i:2 * i + 2]
                self.update_curve()
                return

    def deselect_point(self, event):
        self.selected_point = None
        self.selected_handle = None
        self.update_curve()

    def update_curve(self):
        # 根据控制点和权重点重新计算并绘制Bezier曲线
        self.canvas.delete("curve")
        if len(self.points) > 1:
            if self.curve_type.get() == "N-Bezier":
                # 生成Bezier曲线的控制点列表，包括主控制点和权重控制点
                bezier_points = []
                for i in range(len(self.points)):
                    handle_index = i * 2
                    if i == 0:  # 对于每个主控制点，添加两个权重控制点
                        bezier_points.append(self.points[i])
                        bezier_points.append(self.handle_points[handle_index + 1])
                    elif i < len(self.points) - 1:  # 对于每个主控制点，添加两个权重控制点
                        bezier_points.append(self.handle_points[handle_index])
                        bezier_points.append(self.points[i])
                        bezier_points.append(self.handle_points[handle_index + 1])
                    else:
                        bezier_points.append(self.handle_points[handle_index])
                        bezier_points.append(self.points[i])
                self.draw_bezier_curve(bezier_points)
            elif self.curve_type.get() == "MultiplyBezier":
                for i in range(len(self.points) - 1):
                    bezier_points = []
                    bezier_points.append(self.points[i])
                    bezier_points.append(self.handle_points[i * 2 + 1])
                    bezier_points.append(self.handle_points[(i + 1) * 2])
                    bezier_points.append(self.points[i + 1])
                    self.draw_bezier_curve(bezier_points)

            self.draw_handle_lines()

    def draw_handle_lines(self):
        # 绘制主控制点与权重控制点之间的虚线
        self.canvas.delete("handle_line")  # 删除旧的虚线
        for i in range(len(self.point_ids)):
            point = self.points[i]
            handle_index1 = 2 * i
            handle_index2 = 2 * i + 1
            if handle_index1 < len(self.handle_points) and handle_index2 < len(self.handle_points):
                handle_point1 = self.handle_points[handle_index1]
                handle_point2 = self.handle_points[handle_index2]
                self.canvas.create_line(point, handle_point1, fill="gray", dash=(4, 2), tags="handle_line")
                self.canvas.create_line(point, handle_point2, fill="gray", dash=(4, 2), tags="handle_line")

    def draw_bezier_curve(self, control_points):
        # 绘制Bezier曲线
        n = 100  # 曲线上的点数
        for i in range(n - 1):
            t1 = i / float(n)
            t2 = (i + 1) / float(n)
            p1 = self.compute_bezier_point(t1, control_points)
            p2 = self.compute_bezier_point(t2, control_points)
            self.canvas.create_line(p1, p2, tags="curve", fill="blue")

    def compute_bezier_point(self, t, control_points):
        # 使用De Casteljau算法计算Bezier曲线上的点
        points = [(x, y) for x, y in control_points]
        while len(points) > 1:
            new_points = []
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                new_x = (1 - t) * x1 + t * x2
                new_y = (1 - t) * y1 + t * y2
                new_points.append((new_x, new_y))
            points = new_points
        return points[0]


root = tk.Tk()
root.title("Curve Editor")
app = CurveEditor(root)
root.mainloop()
