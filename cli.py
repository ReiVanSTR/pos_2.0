import asyncclick as click
from datetime import datetime

from tgbot.services.reports.builder import builder
from tgbot.models import Session
from tgbot.models.agregations.sessions_by_date import get_pipeline

__VERSION__ = "1.0.0"
__USER__ = "Ivan"


__ACTIVE_USERS__ = [
    (395430130, "Maks"),
    (556203989, "Egor"),
    (511220960, "Michał"),
    (628515065, "Denys"),
    (551958194, "Illya")
]

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



@users_group.command("all")
def users_all():
    click.secho(__ACTIVE_USERS__)



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
async def employer_report(user_id, from_date, to_date, user):
    try:
        await builder.generate_employer_report(user_id, datetime.fromisoformat(from_date), datetime.fromisoformat(to_date), user)
        click.secho(f"Generated report for {user_id}", fg="green")
        
    except Exception as error:
        click.secho(f"Error in report generating \nError: {error}", fg="red") 
        
if __name__ == "__main__":
    dispatch_cli()