#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import typing as t
from pathlib import Path


def display_flights(flights: t.List[t.Dict[str, t.Any]]) -> None:
    if flights:
        line = "+-{}-+-{}-+".format("-" * 30, "-" * 8)
        print(line)
        print("| {:^30} | {:^8} |".format("Departure Date", "Destination"))
        print(line)
        for flight in flights:
            print(
                "| {:<30} | {:>8} |".format(
                    flight.get("departure_date", ""),
                    flight.get("destination", ""),
                )
            )
        print(line)
    else:
        print("List of flights is empty.")


def create_db(database_path: Path) -> None:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS flights (
            flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            departure_date TEXT NOT NULL,
            aircraft_type_id INTEGER,
            FOREIGN KEY (aircraft_type_id) REFERENCES aircraft_types (id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS aircraft_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL
        )
        """
    )
    conn.close()


def add_flight(
    database_path: Path,
    destination: str,
    departure_date: str,
    aircraft_type_id: int,
) -> None:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO flights (destination, departure_date, aircraft_type_id)
        VALUES (?, ?, ?)
        """,
        (destination, departure_date, aircraft_type_id),
    )
    conn.commit()
    conn.close()


def select_flights(
    database_path: Path, date: str
) -> t.List[t.Dict[str, t.Any]]:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT flights.departure_date, flights.destination, aircraft_types.type
        FROM flights
        JOIN aircraft_types ON flights.aircraft_type_id = aircraft_types.id
        WHERE departure_date = ?
        """,
        (date,),
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
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "filename", action="store", help="The database file name"
    )

    parser = argparse.ArgumentParser("flights")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command")

    create_db(Path("flights.db"))

    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new flight"
    )
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

    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Display all flights"
    )

    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
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
        conn = sqlite3.connect(args.filename)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO aircraft_types (type)
            VALUES (?)
            """,
            (args.aircraft_type,),
        )
        aircraft_type_id = cursor.lastrowid
        conn.commit()
        conn.close()

        add_flight(
            Path(args.filename),
            args.destination,
            args.departure_date,
            aircraft_type_id,
        )

    elif args.command == "display":
        all_flights = select_flights(Path(args.filename), "")
        display_flights(all_flights)

    elif args.command == "select":
        selected_flights = select_flights(Path(args.filename), args.date)
        display_flights(selected_flights)


if __name__ == "__main__":
    main()
