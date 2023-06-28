from functools import reduce
from math import floor
import os
from pathlib import Path
import random
import shutil
from typing import IO

# Define genetic algorithm parameters
POPULATION_SIZE = 500
MUTATION_RATE = 0.02
NUM_GENERATIONS = 20
SHIFTS_COUNT = 6


links: dict[str, list[str]] = {}
preqs: dict[str, list[str]] = {}


def format_solution(solution: dict[int, list[str]]) -> str:
    global task_times, total_divided_by_steps, total_time, links

    shifts_info: dict[int, dict] = dict.fromkeys(solution.keys(), {})

    for shift in solution.items():
        tasks = shift[1]
        shifts_info[shift[0]] = {"tasks": tasks}
        shift_time = sum([task_times[t] for t in tasks])
        shifts_info[shift[0]]["time"] = shift_time
        shifts_info[shift[0]]["dif"] = round(
            abs(shift_time - total_divided_by_steps), 2
        )
    max_shift_time = max([info["time"] for info in shifts_info.values()])
    min_shift_time = min([info["time"] for info in shifts_info.values()])
    total_differences = round(sum([info["dif"] for info in shifts_info.values()]), 2)
    info_map = map(
        lambda info: f"{info[0]+1}: {info[1]['tasks']}, total time = ({info[1]['time']}), dif = ({info[1]['dif']})",
        shifts_info.items(),
    )

    shifts_info_string = reduce(
        lambda x, y: f"{x}\n{y}",
        info_map,
        "",
    )
    shifts_info_string += (
        f"\nTotal time = {total_time}\nTotal_time/Steps ={total_divided_by_steps}\n"
    )

    shifts_info_string += f"Total differences = {total_differences}\nAverage differences = {round(total_differences/SHIFTS_COUNT,2)}\n"
    shifts_info_string += f"Max shift time = {max_shift_time}\n"
    shifts_info_string += f"Min shift time = {min_shift_time}\n"
    shifts_info_string += "=" * 30 + "\n"

    return shifts_info_string


# Define fitness function
def fitness(individual: dict[int, list[str]]):
    global task_times, total_divided_by_steps, total_time, links

    # The total time of each shift tasks.
    shifts_times = [sum(task_times[t] for t in tasks) for tasks in individual.values()]
    total_dif = sum([abs(time - total_divided_by_steps) for time in shifts_times])
    return round(total_dif, 2)


def get_pop() -> dict[int, list[str]]:
    global task_times, total_divided_by_steps, total_time, links, preqs

    tasks_list = [*task_times]
    available_tasks = tasks_list.copy()
    shifts: dict[int, list[str]] = dict.fromkeys([i for i in range(SHIFTS_COUNT)], [])
    last_task = [*task_times][-1]
    # first item in the 1st shift should always be the first task in production line
    c = 0

    while c < SHIFTS_COUNT:
        if len(available_tasks) == 1 or c == SHIFTS_COUNT - 1:
            shifts[c] = shifts[c] + available_tasks
            break
        tasks_without_lastone = available_tasks[:-1]
        rand_task = random.choice(available_tasks if c != 0 else tasks_without_lastone)

        task_sequence: list[str] = getTaskPrerequisites(rand_task, available_tasks)
        if rand_task != last_task:
            task_sequence += getLinkedTasks(rand_task, available_tasks, task_sequence)

        tasks_count_divided_by_shifts_count = floor(len(tasks_list) / SHIFTS_COUNT)
        sorted_task_sequence = sorted(task_sequence, key=lambda x: int(x))

        if len(task_sequence) <= tasks_count_divided_by_shifts_count:
            shift_task_count = random.randint(1, len(task_sequence))
            tasks_to_add = sorted_task_sequence[:shift_task_count]
            shifts[c] = tasks_to_add

        else:
            tasks_to_add = sorted_task_sequence
            tasks_temp = tasks_to_add.copy()
            while True:
                to_add = tasks_temp[:tasks_count_divided_by_shifts_count]
                shifts[c] = to_add
                for t in to_add:
                    tasks_temp.remove(t)
                if len(tasks_temp) < tasks_count_divided_by_shifts_count:
                    break
                c += 1
            if len(tasks_temp) != 0:
                shifts[c] = tasks_temp
                c += 1

        for t in tasks_to_add:
            available_tasks.remove(t)
        c += 1
    if last_task not in shifts[SHIFTS_COUNT - 1]:
        for shift in shifts:
            if last_task in shifts[shift]:
                shift_with_last = shifts[shift]
                last_current_shift = shifts[SHIFTS_COUNT - 1]

                shifts.update(
                    {
                        SHIFTS_COUNT - 1: shift_with_last,
                        shift: last_current_shift,
                    }
                )
                break
    return shifts


def getTaskPrerequisites(task: str, available_tasks: list, limit=None) -> list[str]:
    global task_times, total_divided_by_steps, total_time, links, preqs

    taskHasNoPrerequisites = task not in preqs.keys()
    if taskHasNoPrerequisites:
        return [task]
    # else return [task] with foreach prerequisite to this task
    task_prerequisites = preqs[task]
    result = [task]
    for t in task_prerequisites:
        if t in available_tasks:
            if limit is not None and len(result) == limit:
                break
            result = list(set(getTaskPrerequisites(t, available_tasks) + result))
    return sorted(result)


def getLinkedTasks(task: str, available_tasks: list, current_tasks: list, limit=None):
    global task_times, total_divided_by_steps, total_time, links, preqs

    # if [task] has no linked tasks, return with empty list
    if task not in links.keys():
        return []
    randomLinkedTask = random.choice(links[task])
    result = []
    taskPrerequisitesFinished = True
    for pre in preqs[randomLinkedTask]:
        if pre in available_tasks and (pre not in current_tasks or pre != task):
            taskPrerequisitesFinished = False
    if randomLinkedTask in available_tasks and taskPrerequisitesFinished:
        if limit is not None and len(result) == limit:
            return result
        result += getLinkedTasks(
            randomLinkedTask, available_tasks, current_tasks + [task]
        )
    return result


task_times = {}
total_time = 0
total_divided_by_steps: float = 0


def crossover(parent1: dict[int, list[str]], parent2: dict[int, list[str]]):
    child: dict[int, list[str]] = {}

    tasks_list = [*task_times]
    available_tasks = tasks_list.copy()
    tasks_count_divided_by_shifts_count = floor(len(tasks_list) / SHIFTS_COUNT)
    for shift in range(SHIFTS_COUNT):
        child[shift] = []
        shift_tasks = []
        random_parent: dict[int, list[str]] = random.choice([parent1, parent2])

        for task in random_parent[shift]:
            if len(shift_tasks) == len(random_parent[shift]):
                break
            if task not in available_tasks:
                continue
            taskHasNoPrerequisites = task not in preqs.keys()
            if taskHasNoPrerequisites:
                shift_tasks.append(task)
            else:
                shift_tasks_count = int(len(random_parent[shift]) * random.random())

                shift_tasks = getTaskPrerequisites(
                    task, available_tasks, shift_tasks_count
                )

        for task in shift_tasks:
            available_tasks.remove(task)
        child[shift] = shift_tasks
    return child


def mutation(solution):
    for shift in range(SHIFTS_COUNT):
        for task in range(len(solution[shift])):
            if random.random() < 0.1 and task in preqs.keys():
                solution[shift][task] = random.choice(preqs[solution[shift][task]])
    return solution


def new_solution(parents):
    parent1 = random.choice(parents)
    parent2 = random.choice(parents)
    child = crossover(parent1, parent2)
    return mutation(child)


def executeAlgorithm():
    global task_times, total_time, total_divided_by_steps, preqs
    preqs.clear()
    task_times.clear()
    total_time = 0
    total_divided_by_steps = 0

    tasks = Path(__file__).with_name("tasks.txt")
    links = Path(__file__).with_name("links.txt")
    with tasks.open("r") as tasks_file, links.open("r") as links_file:
        # Read task times from file
        for line in tasks_file.readlines():
            task, time = line.split(",")
            task_times[task] = int(time)
            total_time += int(time)

        # Read links between nodes from file
        links = {}
        for line in links_file.readlines():
            task, link_str = line.split(",")
            # links[task] = link_str.split(";")
            # task, link_str = line.strip().split(",")
            if task in links.keys():
                links[task] += [link_str]
            else:
                links[task] = [link_str]
            if link_str in preqs.keys():
                preqs[link_str] += [task]
            else:
                preqs[link_str] = [task]

        total_divided_by_steps = round(total_time / SHIFTS_COUNT, 2)

        # Initialize the population randomly.
        population: list[dict[int, list[str]]] = [
            get_pop() for _ in range(POPULATION_SIZE)
        ]

        best_fitness = 500.0
        temp_dir = "/tmp/download_files"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        # zip_file_path = f"{temp_dir}/result.zip"
        os.makedirs(temp_dir, exist_ok=True)

        # Open output files
        with open(temp_dir + "/all_results_steps.txt", "w") as all_solutions_file, open(
            temp_dir + "/optimal_results_steps.txt", "w"
        ) as optimal_solutions_file:
            optimal_solutions_file.truncate()
            all_solutions_file.truncate()
            evaluated_population: list[tuple[float, dict[int, list[str]]]] = []
            for gen in range(NUM_GENERATIONS):
                # calculate the fitness of each solution(item) in population
                evaluated_population.clear()
                for individual in population:
                    ind_fitness: float = fitness(individual)
                    formatted_solution = format_solution(individual)

                    all_solutions_file.write(f"{formatted_solution}\n")

                    if ind_fitness <= best_fitness:
                        best_fitness = ind_fitness
                        optimal_solutions_file.write(f"{formatted_solution}\n")

                    evaluated_population.append((ind_fitness, individual))

                evaluated_population.sort(key=lambda x: x[0])
                print(
                    f"==== Generation {gen}: Best solution ==== {format_solution(evaluated_population[0][1])}\n"
                )

                parents: list[dict[int, list[str]]] = [
                    population_info[1] for population_info in evaluated_population[:100]
                ]

                # Create new population by crossover and mutation
                offspring: list[dict[int, list[str]]] = []
                for _ in range(POPULATION_SIZE):
                    offspring.append(new_solution(parents))
                population = offspring
            # all_solutions_file.close()
            # optimal_solutions_file.close()
            return optimal_solutions_file, all_solutions_file
