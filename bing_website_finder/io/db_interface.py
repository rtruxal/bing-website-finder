import sqlite3
from os import path
import csv
import pandas as pd
from bing_website_finder import PKG_ROOT


DB_LOC = path.realpath(path.join(PKG_ROOT, 'data', 'transient.sqlite'))
def get_db():
    db = sqlite3.connect(
        DB_LOC,
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    return db

def _init_db():
    db = get_db()
    schemapth = path.join(PKG_ROOT, 'data', 'schema.sql')
    with open(schemapth, 'r') as schemafile:
        db.executescript(schemafile.read())
    print('initialized the db.')

def read_from_db(statement):
    con = get_db()
    rows = con.execute(statement).fetchall()
    return rows


def company_db_to_csv(outfilepth, verbose=False):
    con = get_db()
    rows = con.execute(
        'SELECT * FROM companies;'
    ).fetchall()
    if path.exists(outfilepth):
        mode = 'a'
    else:
        mode = 'w'
    with open(outfilepth, mode) as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Company Name', 'Website', 'Domain'])
        for row in rows:
            writer.writerow(list(row))
    if verbose:
        print('INFO: successfully wrote companies table to {} using mode: {}'.format(outfilepth, mode))

def csv_to_company_db(infilepth):
    con = get_db()
    cur = con.cursor()
    with open(infilepth, 'r') as infile:
        dr = csv.DictReader(infile)
        to_db = [(i['Company Name'], i['Website']) for i in dr]
    cur.executemany(
        "INSERT INTO companies (company_name, website)"
        " VALUES (?, ?);",
        (to_db)
    )
    con.commit()

def df_to_company_db(df, verbose=False):
    con = get_db()
    _df = df.copy()
    _df.columns = map(lambda x: x.replace('Company Name', 'company_name'), _df.columns)
    _df.columns = map(lambda y: y.replace('Website', 'website'), _df.columns)
    _df.columns = map(lambda z: z.replace('Domain', 'derived_suffix'), _df.columns)
    _df.to_sql('companies', con, index=False, if_exists='append')
    if verbose:
        print('INFO: dataframe successfully inserted into companies.')
    del _df

def df_to_email_db(df, verbose=False):
    con = get_db()
    df.to_sql('emails', con, index=False, if_exists='append')
    if verbose:
        print('INFO: dataframe successfully inserted into emails.')

def get_db_colnames(tablename):
    con = get_db()
    cur = con.execute('SELECT * FROM {};'.format(tablename))
    row = cur.fetchone()
    return list(row.keys())

def company_db_to_df():
    con = get_db()
    try:
        df = pd.read_sql_query(
            "SELECT * FROM companies;",
            con
        )
    except:
        _init_db()
        df = pd.read_sql_query(
            "SELECT * FROM companies;",
            con
        )
    df.columns = map(lambda x: x.replace('company_name', 'Company Name'), df.columns)
    df.columns = map(lambda y: y.replace('website', 'Website'), df.columns)
    df.columns = map(lambda z: z.replace('derived_suffix', 'Domain'), df.columns)
    return df

def email_db_to_df():
    con = get_db()
    df = pd.read_sql_query(
        'SELECT * FROM emails;',
        con
    )
    return df


def db_existance_checks():
    statement = "SELECT name FROM sqlite_master WHERE type='table' AND name='companies';"
    con = get_db()
    try:
        con.execute(statement)
    except:
        _init_db()


if __name__ == "__main__":
    def check_company_db():
        db = get_db()
        foo = db.execute(
            'SELECT * FROM companies;'
        ).fetchall()
        return [(j, k, l) for j,k,l in [i for i in foo]]
    def test_db_create_and_modify():
        db = get_db()
        db.execute(
            'INSERT INTO companies (company_name, website, derived_suffix)'
            ' VALUES (?, ?, ?)',
            ('bobs burgers', 'https://bobsburgers.com/home.aspx', 'bobsburgers.com')
        )
        db.commit()
        vals = check_company_db()
        print(vals)
    def test_convert_csv_to_db():
        infilepth = r'C:\Users\v-rotrux\code\public_repos\mine\bing-website-finder\bing_website_finder\data\example_output2.csv'
        csv_to_company_db(infilepth)
        vals = check_company_db()
        print(vals)
    def test_convert_df_to_db():
        df = pd.read_csv(r'C:\Users\v-rotrux\code\public_repos\mine\bing-website-finder\bing_website_finder\data\example_output2.csv')
        df_to_company_db(df)
        # print(df.columns)
        vals = check_company_db()
        print(vals)
    def test_convert_db_to_df():
        df = company_db_to_df('companies')
        print(df)
        print(df.columns)
    def test_convert_db_to_csv():
        outfile = r'C:\Users\v-rotrux\code\public_repos\mine\bing-website-finder\bing_website_finder\data\example_output3.csv'
        company_db_to_csv(outfile, verbose=True)

    ## _init_db()
    # check_company_db()
    # test_db_create_and_modify()
    # test_convert_csv_to_db()
    # test_convert_df_to_db()
    # test_convert_db_to_df()
    # test_convert_db_to_csv()