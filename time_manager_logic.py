import json
from datetime import datetime

class Task:
    def __init__(self, name, expected_time):
        self.name = name
        self.expected_time = expected_time
        self.actual_time = 0
        self.start_time = None

    def start(self):
        if not self.start_time:
            self.start_time = datetime.now()

    def stop(self):
        if self.start_time:
            self.actual_time += (datetime.now() - self.start_time).total_seconds() / 3600
            self.start_time = None

    def to_dict(self):
        return {
            "任务名称": self.name,
            "预期时间": self.expected_time,
            "实际时间": self.actual_time
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(data["任务名称"], data["预期时间"])
        task.actual_time = data["实际时间"]
        return task

class TimeManager:
    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def add_task(self, name, expected_time):
        if expected_time <= 0:
            expected_time = 0.5  # 如果预期时间小于等于0，设置为0.5小时
        task = Task(name, expected_time)  # 不再乘以3600
        self.tasks.append(task)
        self.save_tasks()

    def edit_task(self, index, name, expected_time):
        if 0 <= index < len(self.tasks):
            expected_time = max(0.5, expected_time)  # 确保预期时间至少为0.5小时
            self.tasks[index].name = name
            self.tasks[index].expected_time = expected_time  # 不再乘以3600

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_tasks()

    def start_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].start()

    def stop_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].stop()
            self.save_tasks()

    def get_statistics(self):
        total_expected = sum(task.expected_time for task in self.tasks)
        total_actual = sum(task.actual_time for task in self.tasks)
        efficiency = (total_actual / total_expected * 100) if total_expected > 0 else 0

        return {
            "总预期时间": total_expected,
            "总实际时间": total_actual,
            "效率": efficiency
        }

    def save_tasks(self):
        tasks_data = [task.to_dict() for task in self.tasks]
        try:
            with open("任务.json", "w", encoding="utf-8") as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务时出现错误：{str(e)}")

    def load_tasks(self):
        try:
            with open("任务.json", "r", encoding="utf-8") as f:
                data = f.read()
                if data:
                    tasks_data = json.loads(data)
                    self.tasks = []
                    for task_data in tasks_data:
                        # 检查是否存在 '完成时间' 字段，如果不存在则添加
                        if '完成时间' not in task_data:
                            task_data['完成时间'] = None
                        self.tasks.append(Task.from_dict(task_data))
                else:
                    self.tasks = []
        except FileNotFoundError:
            self.tasks = []
        except json.JSONDecodeError:
            print("任务文件格式错误，创建新的任务列表")
            self.tasks = []
        except Exception as e:
            print(f"加载任务时出现错误：{str(e)}")
            self.tasks = []