import os
import re
from app.settings import STATIC_URL


def parse_latex():
    folder_path = os.path.join(STATIC_URL, "latex")
    parsed_data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".tex"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # extract tasks and solutions
                task_regex = r"\\begin\{task\}.*?\n(.*?)\\end\{task\}"
                solution_regex = r"\\begin\{solution\}.*?\n(.*?)\\end\{solution\}"
                tasks = re.findall(task_regex, content, re.DOTALL)
                solutions = re.findall(solution_regex, content, re.DOTALL)
                # extract math equation from each solution and remove unwanted parts from tasks
                for solution in solutions:
                    equation_regex = r"\\begin\{equation\*\}(.*?)\\end\{equation\*\}"
                    equation = re.search(equation_regex, solution, re.DOTALL).group(1)
                    # remove leading and trailing whitespaces
                    equation = equation.strip()
                    # remove unwanted parts from task and extract image filename
                    task = tasks.pop(0).strip().replace(r'\begin{equation*}', '').replace(r'\end{equation*}', ''). \
                        replace('\n', '').replace('\\\\', '')
                    task = re.sub(r'\s{2,}', ' ', task)
                    # extract image filename
                    image_regex = r'\\includegraphics\{.*?/([^/]*?\.jpg)\}'
                    match = re.search(image_regex, task)
                    if match:
                        image = match.group(1)
                        task = re.sub(r'\\includegraphics\{.*?/[^/]*?\.jpg\}', '', task)
                    else:
                        image = None
                    # create dictionary for each task-solution pair
                    task_dict = {'task': task.strip(), 'solution': equation.strip(), 'image': image,
                                 'batch': filename[:-4]}
                    parsed_data.append(task_dict)
    print(parsed_data)
