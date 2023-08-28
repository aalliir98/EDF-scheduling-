import copy
import heapq
import math
import random


class LCM:
    def lcm(self, a, b):
        return (a * b) // math.gcd(a, b)

    def lcm_of_array(self, numbers):
        if len(numbers) == 0:
            return None

        result = numbers[0]
        for num in numbers[1:]:
            result = self.lcm(result, num)

        return result


class Task:
    def __init__(self, name, period, deadline):
        self.name = name
        self.period = period
        self.execution_time = 0
        self.deadline = deadline
        self.space = 100
        self.sub_tasks = []
        self.next_deadline = deadline
        self.next_period = 0

    def __lt__(self, other):
        if self.next_deadline < other.next_deadline:
            return True
        elif self.next_deadline == other.next_deadline:
            return self.next_period < other.next_period
        return False

    def __str__(self):
        return (
            f" Task: {self.name}\n"
            f" Period: {self.period}\n"
            f" Execution Time: {self.execution_time}\n"
            f" Deadline: {self.deadline}\n"
            f" Next Deadline: {self.next_deadline}\n"
            f" Next Period: {self.next_period}\n"
        )

    def execute_default(self):
        current_time = 0
        space = self.space
        sub_tasks = self.sub_tasks
        executing_subtasks = []
        executing_space = []
        for sub_task in sub_tasks:
            while not sub_task.execute_start:
                if sub_task.space <= space:
                    space -= sub_task.space
                    current_time += sub_task.configuration_time
                    sub_task.end_time = current_time + sub_task.execute_time
                    sub_task.execute_start = True
                    executing_subtasks.append(sub_task)

                elif sub_task.space > space:
                    for sub_task2 in executing_subtasks:
                        if sub_task2.end_time < current_time:
                            space += sub_task2.space
                            sub_task2.execute_end = True
                            executing_subtasks.remove(sub_task2)
                            if sub_task.space < space:
                                break
                if sub_task.space > space and not sub_task.execute_start:
                    while sub_task.space > space:
                        minimum_subtask = min(executing_subtasks, key=lambda subtask: subtask.end_time)
                        current_time = minimum_subtask.end_time
                        space += minimum_subtask.space
                        minimum_subtask.execute_end = True
                        executing_subtasks.remove(minimum_subtask)

        for _ in range(len(executing_subtasks)):
            minimum_subtask = min(executing_subtasks, key=lambda subtask: subtask.end_time)
            current_time = minimum_subtask.end_time
            space += minimum_subtask.space
            minimum_subtask.execute_end = True
            executing_subtasks.remove(minimum_subtask)

        for sub_task in sub_tasks:
            sub_task.end_time = 0
            sub_task.execute_start = False
            sub_task.execute_end = False
        self.execution_time = current_time

    def execute_advanced(self):
        current_time = 0
        space = self.space
        sub_tasks = self.sub_tasks
        executing_subtasks = []
        executing_space = []
        for sub_task in sub_tasks:
            while not sub_task.execute_start:
                if sub_task.space <= space:
                    space -= sub_task.space
                    executing_space.append([[current_time, current_time + sub_task.configuration_time], 100])
                    current_time += sub_task.configuration_time
                    sub_task.end_time = current_time + sub_task.execute_time
                    executing_space.append([[current_time, sub_task.end_time], sub_task.space])
                    sub_task.execute_start = True
                    executing_subtasks.append(sub_task)

                elif sub_task.space > space:
                    for sub_task2 in executing_subtasks:
                        if sub_task2.end_time < current_time:
                            space += sub_task2.space
                            sub_task2.execute_end = True
                            executing_subtasks.remove(sub_task2)
                            if sub_task.space < space:
                                break
                if sub_task.space > space and not sub_task.execute_start:
                    while sub_task.space > space:
                        minimum_subtask = min(executing_subtasks, key=lambda subtask: subtask.end_time)
                        current_time = minimum_subtask.end_time
                        space += minimum_subtask.space
                        minimum_subtask.execute_end = True
                        executing_subtasks.remove(minimum_subtask)

        for _ in range(len(executing_subtasks)):
            minimum_subtask = min(executing_subtasks, key=lambda subtask: subtask.end_time)
            current_time = minimum_subtask.end_time
            space += minimum_subtask.space
            minimum_subtask.execute_end = True
            executing_subtasks.remove(minimum_subtask)

        for sub_task in sub_tasks:
            sub_task.end_time = 0
            sub_task.execute_start = False
            sub_task.execute_end = False
        self.execution_time = current_time
        free_intervals = calculate_free_space(executing_space, self.execution_time)
        return free_intervals


class SubTask:
    def __init__(self, task, name, configuration_time, execute_time, space):
        self.task = task
        self.name = name
        self.execute_time = execute_time
        self.configuration_time = configuration_time
        self.space = space
        self.end_time = 0
        self.execute_start = False
        self.execute_end = False


def use_free_space(task, free_intervals):
    for sub_task in task.sub_tasks:
        for free_interval in free_intervals:
            if sub_task.space <= free_interval[1] and sub_task.configuration_time <= (
                    free_interval[0][1] - free_interval[0][0]):
                free_interval[0][0] += sub_task.configuration_time
                if free_interval[0][0] == free_interval[0][1]:
                    free_intervals.remove(free_interval)
                sub_task.configuration_time = 0
                break


class EDFScheduler:
    def __init__(self):
        self.bag_of_tasks = []
        self.ready_tasks = []
        self.current_time = 0
        self.save = []

    def add_task(self, task):
        heapq.heappush(self.bag_of_tasks, task)

    def run_default(self, total_time):
        ready_tasks = copy.deepcopy(self.ready_tasks)
        bag_of_tasks = copy.deepcopy(self.bag_of_tasks)
        self.current_time = 0
        # for task in bag_of_tasks:
        #     print(task)
        # print("-----------------------------------------------------------------\n")
        number_of_missed_tasks = 0
        number_of_all_executed_tasks = 0
        while self.current_time < total_time:
            # ready task is for tasks which their request is received
            for task in bag_of_tasks:
                if self.current_time >= task.next_period:
                    heapq.heappush(ready_tasks, task)
            if not ready_tasks:
                min_task = min(bag_of_tasks, key=lambda task2: task2.next_period)
                self.current_time = min_task.next_period
                continue
            # sort to find minimum deadline
            ready_tasks.sort()
            task = heapq.heappop(ready_tasks)
            if self.current_time + task.execution_time >= task.next_deadline:
                # print(f"Missed deadline for Task {task.name} at time {self.current_time}\n")
                # if self.current_time < task.next_deadline:
                #     self.current_time = task.next_deadline
                task.next_period += task.period
                task.next_deadline += task.deadline
                number_of_missed_tasks += 1
            else:
                # print(f"task before execution:\n{task}")
                # print(f"Running Task {task.name} at time {self.current_time}\n")
                task.execute_default()
                task.next_deadline += task.deadline
                task.next_period += task.period
                self.current_time += task.execution_time
                # print(f"current time after execution: {self.current_time}\n")
                # print(f"task after execution:\n{task}")
            number_of_all_executed_tasks += 1
            ready_tasks.clear()
            # print("---------------------------------------------------------------\n")
        self.save.append(number_of_missed_tasks)
        self.save.append(number_of_all_executed_tasks)
        self.save.append(number_of_missed_tasks * 100 / number_of_all_executed_tasks)

    def run_advanced(self, total_time):
        free_intervals = []
        ready_tasks = copy.deepcopy(self.ready_tasks)
        bag_of_tasks = copy.deepcopy(self.bag_of_tasks)
        self.current_time = 0
        # for task in bag_of_tasks:
        #     print(task)
        # print("-----------------------------------------------------------------\n")
        number_of_missed_tasks = 0
        number_of_all_executed_tasks = 0
        while self.current_time < total_time:
            task_copy = None
            # ready task is for tasks which their request is received
            for task in bag_of_tasks:
                if self.current_time >= task.next_period:
                    heapq.heappush(ready_tasks, task)
            if not ready_tasks:
                min_task = min(bag_of_tasks, key=lambda task2: task2.next_period)
                self.current_time = min_task.next_period
                continue
            # sort to find minimum deadline
            ready_tasks.sort()
            task = heapq.heappop(ready_tasks)

            task_copy = copy.deepcopy(task)
            use_free_space(task, free_intervals)
            free_intervals = task.execute_advanced()

            if self.current_time + task.execution_time >= task.next_deadline:
                # print(f"Missed deadline for Task {task.name} at time {self.current_time}\n")
                # if self.current_time < task.next_deadline:
                #     self.current_time = task.next_deadline
                task.next_period += task.period
                task.next_deadline += task.deadline
                number_of_missed_tasks += 1
            else:
                # print(f"task before execution:\n{task}")
                # print(f"Running Task {task.name} at time {self.current_time}\n")

                self.current_time += task.execution_time
                task.next_deadline += task.deadline
                task.next_period += task.period
                # print(f"current time after execution: {self.current_time}\n")
                # print(f"task after execution:\n{task}")

            task.sub_tasks = task_copy.sub_tasks
            number_of_all_executed_tasks += 1
            ready_tasks.clear()
            # print("---------------------------------------------------------------\n")
        self.save.append(number_of_missed_tasks)
        self.save.append(number_of_all_executed_tasks)
        self.save.append(number_of_missed_tasks * 100 / number_of_all_executed_tasks)


def create_random_task():
    bag_of_tasks = []
    tasks_numbers = random.randint(3, 10)
    while len(bag_of_tasks) != tasks_numbers:
        period = random.randint(7, 15) * 5
        deadline = period
        task = Task("Task " + chr(random.randint(65, 90)), period=period, deadline=deadline)
        subtasks = []
        subtasks_numbers = random.randint(3, 8)
        for i in range(subtasks_numbers):
            configuration_time = random.randint(3, 8)
            execute_time = random.randint(3, 10)
            space = random.randint(5, 70)
            subtask = SubTask(task, "Subtask " + chr(random.randint(65, 90)), configuration_time, execute_time, space)
            subtasks.append(subtask)
        task.sub_tasks = subtasks
        task.execute_default()
        if task.period > task.execution_time:
            bag_of_tasks.append(task)
    return bag_of_tasks


def main():
    lcm = LCM()
    for i in range(10):
        bag_of_tasks = create_random_task()
        scheduler = EDFScheduler()
        for task in bag_of_tasks:
            scheduler.add_task(task)
        times = [task.period for task in bag_of_tasks]
        total_time = lcm.lcm_of_array(times)
        scheduler.run_default(total_time)
        scheduler.run_advanced(total_time)

        print(f"missed default:  {scheduler.save[0]}")
        print(f"all default: {scheduler.save[1]}")
        print(f"percentage default: {scheduler.save[2]}")
        print(f"missed advance:  {scheduler.save[3]}")
        print(f"all advance: {scheduler.save[4]}")
        print(f"percentage advance: {scheduler.save[5]}")
        print("------------------------------------------------------")


def calculate_free_space(intervals, total_time):
    interval_space = [100] * (total_time + 1)

    for interval in intervals:
        start_time, end_time = interval[0]
        space_token = interval[1]
        space_taken = space_token

        for i in range(start_time, end_time):
            interval_space[i] -= space_taken
            if interval_space[i] < 0:
                interval_space[i] = 0

    free_intervals = []
    current_interval_start = 0
    current_interval_space = interval_space[0]

    for i in range(1, total_time):
        if interval_space[i] != current_interval_space:
            free_intervals.append([[current_interval_start, i], current_interval_space])
            current_interval_start = i
            current_interval_space = interval_space[i]

    free_intervals.append([[current_interval_start, total_time], current_interval_space])

    return free_intervals


if __name__ == '__main__':
    main()
