import logging
from datetime import datetime, timedelta
from typing import Dict
from pymongo.results import InsertOneResult
import asyncclick as click


from tgbot.models.session import Session
from tgbot.models.bills import Bills
from tgbot.models.order import OrderData
from tgbot.models.user import User
from tgbot.models.tabacco import Tabacco
from tgbot.models.shift import Shift
from tgbot.models.editing_order import EditingOrder



async def update_session_day(session_date: str, user_id: int, work_time: Dict[str, int], sellings: Dict[int, int]):

    bills = []

    for cost, quantity in sellings.items():
        for _ in range(quantity):
            bills.append(
                OrderData(
                     _id = "",
                    order_name = "Edited Hookah",
                    created_by = user_id,
                    timestamp = datetime.fromisoformat(session_date) + timedelta(hours = 8, minutes=5),
                    cart = [{"66a54931a2b03d9ce8fb085b":16}],
                    cost = cost
                )
            )


    session_id = await Session.find_session_by_date(datetime.fromisoformat(session_date))
    if session_id:
        click.secho(f"Session already created, ID: {session_id}", fg="red")
        session = await Session.open_session_by_id(session_id)

    if not session_id:
        click.secho(f"Opening session by date {session_date}", fg="green")
        session = await Session.open_session_by_day(datetime.fromisoformat(session_date), user_id)

    shift: InsertOneResult = await Shift.create_shift_by_date(user_id, session_date+"T08:00:00", work_time)
    click.secho(f"Created shift {shift} with work time: {work_time}", fg="green")
    await User.update_shift(user_id, shift.inserted_id)
    
    for raw_bill in bills:
        order = await EditingOrder.create_order(**raw_bill.to_dict())
        bill = await Bills.create_bill(bill_name = "Edited Bill", user_id=user_id, timestamp=datetime.fromisoformat(session_date)+timedelta(hours=8, minutes=3), orders = [order])
        click.secho(f"""
            Created orders: {order},\n
            Bill {bill} Map: user:{user_id}, timestamp:{datetime.fromisoformat(session_date)+timedelta(hours=8, minutes=3)}
        """, fg="blue")
        await Bills.close_bill(bill, "cash")
        await Session.update_session_bills([bill])
        click.secho(f"Updated session {session_id} with bill chain {bill}", fg="blue")
        tabacco = await Tabacco.get_by_id("66a54931a2b03d9ce8fb085b")
        await Tabacco.update_weight(tabacco._id, tabacco.weight - 10)
        click.secho(f"Updated tabacco weight 66a54931a2b03d9ce8fb085b", fg="blue")
    await Session.close_session(session_id, user_id)
    click.secho(f"Closed session by {user_id}, Transaction id: {session_id}", fg="green")