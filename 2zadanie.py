import argparse
import typing as t

import psycopg2


DATABASE = "postgres"
USER = "postgres"
PASSWORD = "zxcgfd32"


def display_flights(flights: t.List[t.Dict[str, t.Any]]) -> None:
    if flights:
        line = "+-{}-+-{}-+-{}-+".format("-" * 30, "-" * 30, "-" * 12)
        print(line)
        print(
            "| {:^30} | {:^30} | {:^12} |".format(
                "Departure Date", "Destination", "Aircraft Type"
            )
        )
        print(line)
        for flight in flights:
            print(
                "| {:<30} | {:<30} | {:<12} |".format(
                    flight.get("departure_date", ""),
                    flight.get("destination", ""),
                    flight.get("aircraft_type", ""),
                )
            )
        print(line)
    else:
        print("List of flights is empty.")


def add_flight(
    destination: str, departure_date: str, aircraft_type: str
) -> None:
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM aircraft_types WHERE type = %s
        """,
        (aircraft_type,),
    )
    aircraft_type_row = cursor.fetchone()
    if aircraft_type_row:
        aircraft_type_id = aircraft_type_row[0]
    else:
        cursor.execute(
            """
            INSERT INTO aircraft_types (type) VALUES (%s) RETURNING id
            """,
            (aircraft_type,),
        )
        aircraft_type_id = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO flights (destination, departure_date, aircraft_type_id)
        VALUES (%s, %s, %s)
        """,
        (destination, departure_date, aircraft_type_id),
    )
    conn.commit()
    conn.close()


def select_flights(date: str = None) -> t.List[t.Dict[str, t.Any]]:
    conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD)
    cursor = conn.cursor()
    if date:
        cursor.execute(
            """
            SELECT flights.departure_date, flights.destination, aircraft_types.type
            FROM flights
            JOIN aircraft_types ON flights.aircraft_type_id = aircraft_types.id
            WHERE departure_date = %s
            """,
            (date,),
        )
    else:
        cursor.execute(
            """
            SELECT flights.departure_date, flights.destination, aircraft_types.type
            FROM flights
            JOIN aircraft_types ON flights.aircraft_type_id = aircraft_types.id
            """
        )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "departure_date": row[0],
            "destination": row[1],
            "aircraft_type": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    parser = argparse.ArgumentParser("flights")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser("add", help="Add a new flight")
    add.add_argument(
        "-d",
        "--destination",
        action="store",
        required=True,
        help="Destination of the flight",
    )
    add.add_argument(
        "-dd",
        "--departure_date",
        action="store",
        required=True,
        help="Departure date of the flight",
    )
    add.add_argument(
        "-at",
        "--aircraft_type",
        action="store",
        required=True,
        help="Aircraft type of the flight",
    )

    _ = subparsers.add_parser("display", help="Display all flights")

    select = subparsers.add_parser(
        "select",
        help="Select flights by departure date",
    )
    select.add_argument(
        "-D",
        "--date",
        action="store",
        required=True,
        help="Departure date to select flights",
    )

    args = parser.parse_args(command_line)

    if args.command == "add":
        add_flight(args.destination, args.departure_date, args.aircraft_type)

    elif args.command == "display":
        all_flights = select_flights()
        display_flights(all_flights)

    elif args.command == "select":
        selected_flights = select_flights(args.date)
        display_flights(selected_flights)


if __name__ == "__main__":
    main()
