# pylint: disable=C0302

"""
Chron.
Copyright (C) 2020 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
Daniil Mordasov, Liam O’Flynn, Mikhail Orlov.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from celery import current_app

from django.http import JsonResponse


def stv_tasks(request, task_id):
    """ Return result from task """
    task = current_app.AsyncResult(task_id)
    response_data = {"task_status": task.status, "task_id": task.id}
    status = 200
    if task.ready():
        result = task.get()
        response_data = result["response"]
        status = result["status"]
        # Remove this task
        task.forget()

    return JsonResponse(response_data, status=status)
