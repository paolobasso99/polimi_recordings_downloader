import typer
import re

def validate_academic_year(value: str):
    academic_year_r = re.compile("^[0-9]{4}-[0-9]{2}$")
    if academic_year_r.match(value) is None:
        raise typer.BadParameter('The course academic year must be in the format "2021-22".')
    return value