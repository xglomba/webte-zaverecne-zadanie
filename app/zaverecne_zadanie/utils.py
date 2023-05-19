import csv
import re

from django.http import HttpResponse
from sympy import simplify, Eq, latex
from sympy.parsing.latex import parse_latex as pl

def parse_latex(path):
    parsed_data = []
    with open(path, 'r', encoding='utf-8') as file:
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
            task_dict = {'task': task.strip(), 'solution': equation.strip(), 'image': image}
            parsed_data.append(task_dict)
    return parsed_data


def export_task_submissions_to_csv(task_submissions):
    # Define the CSV field names
    field_names = ['task_id', 'batch_name', 'first_name', 'last_name', 'ais_id', 'points']

    # Create the HTTP response object with CSV content type and attachment
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="task_submissions.csv"'

    # Write the CSV data to the response
    writer = csv.DictWriter(response, fieldnames=field_names)
    writer.writeheader()
    for submission in task_submissions:
        writer.writerow({
            'task_id': submission.task.id,
            'batch_name': submission.task.batch.name,
            'first_name': submission.user.first_name,
            'last_name': submission.user.last_name,
            'ais_id': submission.user.ais_id,
            'points': submission.points,
        })
    return response


def compare_equations(solution, student_solution):

    expr1 = pl(student_solution)
    expr2 = pl(solution)

    simplified_expr1 = simplify(expr1)
    simplified_expr2 = simplify(expr2)

    equation1 = Eq(simplified_expr1, 0)
    equation2 = Eq(simplified_expr2, 0)

    return equation1 == equation2
