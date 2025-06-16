import asyncclick as click
from datetime import datetime

from tgbot.services.reports.builder import builder
from tgbot.models import Session, Tabacco
from tgbot.models.agregations.sessions_by_date import get_pipeline
from ast import literal_eval

__VERSION__ = "1.0.0"
__USER__ = "Ivan"


__ACTIVE_USERS__ = [
    (395430130, "Maks"),
    (556203989, "Egor"),
    (511220960, "Michał"),
    (628515065, "Denys"),
    (551958194, "Illya"),
    (6948795534, "Jorgio")
]
#[{"100":10, "cart":[{"Maui":10}]}]

@click.group()
@click.version_option(version = __VERSION__)
def dispatch_cli():
    """Command-line interface to Dispatch."""
    # click.secho(__VERSION__)


@dispatch_cli.group("reports")
def reports_group():
    pass

@dispatch_cli.group("users")
def users_group():
    pass

@dispatch_cli.group("tabacco")
def tabacco_group():
    pass


@users_group.command("all")
def users_all():
    click.secho(""" Ż """)



@reports_group.command("periodic_report")
@click.option(
    "--from_date", prompt = "From date [yyyy-mm-dd]", type = str
)
@click.option(
    "--to_date", prompt = "To date [yyyy-mm-dd]", type = str
)
@click.option(
    "--user", prompt = True, prompt_required = False, default = __USER__, type = str
)
async def periodic_report(from_date, to_date, user):
    from_date = datetime.fromisoformat(from_date)
    to_date = datetime.fromisoformat(to_date)
    _result =  Session._collection.aggregate(get_pipeline(from_date, to_date))
    
    if not _result:
        raise ValueError("No data")
        
    session_data = []
    async for obj in _result:
        session_data.append(obj)
        
    click.confirm(f"Sessions for build report is: {len(session_data)}. Continue?", abort=True)
    
    users = []
    for session in session_data:
        await builder.generate_change_report(session_id=session.get("id"), user_name=user, filename=session.get("date"))
        users.append(session.get("user"))
    
    click.secho("Sucessful!", fg = "green")
    click.confirm(f"Generate employer reports? ", show_default=True, abort=True)
    
    for user in set(users):
        await builder.generate_employer_report(user, from_date,to_date, user)
        
    click.secho("Sucessful!", fg = "green")
        
        

@reports_group.command("employer_report")
@click.option(
    "--user_id", prompt = True, type = int
)
@click.option(
    "--from_date", prompt = "From date [yyyy-mm-dd]", type = str
)
@click.option(
    "--to_date", prompt = "To date [yyyy-mm-dd]", type = str
)
@click.option(
    "--user", prompt = True, prompt_required = False, default = __USER__, type = str
)
@click.option(
    "--by_hours", prompt = "Wg godzin: [y/n]", type = str, default = "n"
)
@click.option(
    "--shift_cost", prompt = True, prompt_required = False, default = 150, type = int
)
@click.option(
    "--hour_cost", prompt = "Stawka godzinowa: ", type = int, default = 22
)
@click.option(
    "--comment", prompt = "Comment: ", type = str
)
async def employer_report(user_id, from_date, to_date, user, by_hours, shift_cost, hour_cost, comment):
    try:
        if by_hours == "y":
            by_hours = True
        else:
            by_hours = False
            
        await builder.generate_employer_report(user_id, datetime.fromisoformat(from_date), datetime.fromisoformat(to_date), user, None, shift_cost, hour_cost, by_hours, comment)
        click.secho(f"Generated report for {user_id}", fg="green")
        
    except Exception as error:
        click.secho(f"Error in report generating \nError: {error}", fg="red")

@reports_group.command("employer_add_shift")
@click.option(
    "--user_id", prompt = True, type = int
)
@click.option(
    "--date", prompt = "Date [yyyy-mm-dd]", type = str
)
@click.option(
    "--work_time", prompt = "Work time hh:mm", type = str
)
@click.option(
    "--sellings", prompt = "Dict cost:quantity", type = click.UNPROCESSED
)

@click.option(
    "--updated_by", prompt = True, prompt_required = False, default = __USER__, type = str
)
async def employer_add_shift(user_id, date, work_time, sellings, updated_by):
    from tgbot.services.reports.editing import update_session_day

    sellings = literal_eval(sellings)
    # cart = literal_eval(cart)
    work_time = work_time.split(":")
    work_time = {
        "hours":int(work_time[0]),
        "minutes":int(work_time[1])
    }

    try:
        await update_session_day(date, user_id, work_time, sellings)
        click.secho(f"\n Added new work shift for {user_id}", fg="green")
    except Exception as e:
        click.secho(f"\n Error {e}", fg="red")

@tabacco_group.command("add_tabacco")
@click.option(
    "--brand", prompt = "Brand name: ", type = str
)
@click.option(
    "--label", prompt = "Label name: ", type = str
)
@click.option(
    "--type_id", prompt = "Premium[1], Standart[2], Mix[3], Pasta[4], Węgiel[5]", type = int
)
@click.option(
    "--weight", prompt = "Invent weight", type = int, default = None
)
@click.option(
    "--is_showed", prompt = "y/n", type = str, default = "n"
)
async def add_tabacco(brand, label, type_id, weight, is_showed):
    types = {
        1:"Premium",
        2:"Standart",
        3:"Mix",
        4:"Pasta",
        5:"Węgiel"
    }
    type = types.get(type_id, None)
    if not type:
        return click.secho(f"Invalid type id", fg="red")

    if await Tabacco.get_by_label(label):
        return click.secho(f"Label {label} already exists", fg="red")
    
    obj_id = await Tabacco.create_tabacco(label, brand, type)
    click.secho(f"Created tabacco {type} {brand}-{label}", fg="green")

    if weight:
        await Tabacco.update_weight(obj_id, weight)
        click.secho(f"Updated weight for tabacco {type} {brand}-{label} weight {weight}g", fg="green")


    if is_showed == "y":
        await Tabacco.change_visibility(obj_id)
        click.secho(f"Visibility is changed, True", fg="green")

    
#{50:1, 45:2} 585708940
if __name__ == "__main__":
    dispatch_cli()