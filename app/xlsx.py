from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet
import os
from typing import List, Dict
from Recording import Recording


def _divide_in_courses(recordings: List[Recording]) -> Dict[str, List[Recording]]:
    """Divide the recordings according to the course and sort them.

    Args:
        recordings (List[Recording]): List of recordings.

    Returns:
        Dict[str, List[Recording]]: A disctionary with as key the course name and
        list of recordings as value.
    """
    courses: Dict[str, List[Recording]] = {}

    for r in recordings:
        key: str = f"{r.course} {r.accademic_year}"
        if key not in courses.keys():
            courses[key] = []

        courses[key].append(r)

    # Sort recordings
    for course in courses.keys():
        courses[course] = sorted(courses[course])

    return courses


def generate_xlsx(recordings: List[Recording], output_folder: str) -> None:
    """Create the xlsx file.

    Args:
        recordings (List[Recording]): List of recordings.
        output_folder (str): Output folder path.
    """
    courses: Dict[str, List[Recording]] = _divide_in_courses(recordings)

    for course, recordings in courses.items():
        course_output_path: str = os.path.join(output_folder, course)
        if not os.path.exists(course_output_path):
            os.makedirs(course_output_path)

        workbook: Workbook = Workbook(
            os.path.join(course_output_path, course + ".xlsx")
        )
        worksheet: Worksheet = workbook.add_worksheet()
        worksheet.set_column(0, 1, 14)
        worksheet.set_column(2, 2, 80)
        worksheet.set_row(0, 17)

        # Write header
        header = workbook.add_format(
            {
                "font_name": "Calibri",
                "bold": True,
                "font_color": "white",
                "font_size": 12,
                "bg_color": "#4F81BD",
                "align": "center",
                "valign": "vcenter",
            }
        )
        worksheet.write(0, 0, "Accademic year", header)
        worksheet.write(0, 1, "Recording date", header)
        worksheet.write(0, 2, "Subject", header)

        # Write rows
        body = workbook.add_format(
            {"font_name": "Calibri", "font_size": 11, "valign": "vcenter"}
        )
        body.set_text_wrap()
        for row, recording in enumerate(recordings):
            worksheet.write(row + 1, 0, recording.accademic_year, body)
            worksheet.write(
                row + 1,
                1,
                recording.recording_datetime.strftime("%Y-%m-%d %H:%M"),
                body,
            )
            worksheet.write(row + 1, 2, recording.subject, body)

        workbook.close()
