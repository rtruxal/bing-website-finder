DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS emails;

CREATE TABLE companies (
    company_name VARCHAR NOT NULL,
    website VARCHAR NULL,
    derived_suffix VARCHAR NULL
);

CREATE TABLE emails (
    email VARCHAR NOT NULL,
    company_name VARCHAR NOT NULL,
    person_name VARCHAR NULL,
    person_title VARCHAR NULL,
    FOREIGN KEY (company_name) REFERENCES companies (company_name)
);