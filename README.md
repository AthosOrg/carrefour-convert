This tool converts the [data provided by Carrefour](https://github.com/ging/carrefour_basket_data_challenge)
for the 2016 TADHack into an SQLite database with the following schema:

    CREATE TABLE purchases(
        id           int primary key,
        mall         int                 not null,
        date         int                 not null,
        client       int
    );
    CREATE TABLE items(
        id           int primary key,
        purchase_id  int                 not null,
        description  text                not null,
        cost         decimal(20,10)      not null,
        amount       int                 not null
    );


Requirements
============

Install the dependencies using `pip install -r requirements.txt`

Usage
=====

`./convert.py INPUT`

`INPUT` is the json file provided by Carrefour.