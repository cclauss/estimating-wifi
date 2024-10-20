-- This code creates a table for data pulled directly from IMLS.
-- We are using it to look up library information for use in the interface.
-- Copying new data in requires pulling a CSV from IMLS and restarting the database.

-- FIXME: This is a horrible process. It is not sustainable long-term.

DROP TABLE IF EXISTS data.imls_data;

CREATE TABLE data.imls_data (
    STABR CHAR(2),
    FSCSKEY CHAR(6),
    FSCS_SEQ INTEGER,
    C_FSCS CHAR(1),
    LIBID VARCHAR(64),
    LIBNAME VARCHAR(256),
    ADDRESS VARCHAR(256),
    CITY VARCHAR(32),
    ZIP CHAR(5),
    ZIP4 CHAR(4),
    CNTY VARCHAR(64),
    PHONE CHAR(10),
    C_OUT_TY CHAR(2),
    SQ_FEET INTEGER,
    F_SQ_FT CHAR(4),
    L_NUM_BM INTEGER,
    HOURS INTEGER,
    F_HOURS CHAR(4),
    WKS_OPEN INTEGER,
    F_WKSOPN CHAR(4),
    YR_SUB INTEGER,
    OBEREG INTEGER,
    STATSTRU INTEGER,
    STATNAME INTEGER,
    STATADDR INTEGER,
    LONGITUD FLOAT,
    LATITUDE FLOAT,
    INCITSST INTEGER,
    INCITSCO INTEGER,
    GNISPLAC VARCHAR(6),
    CNTYPOP INTEGER,
    LOCALE VARCHAR(2),
    CENTRACT FLOAT,
    CENBLOCK INTEGER,
    CDCODE INTEGER,
    CBSA INTEGER,
    MICROF CHAR(1),
    GEOSTATUS CHAR(1),
    GEOSCORE FLOAT,
    GEOMTYPE VARCHAR(32),
    C19WKSCL INTEGER,
    C19WKSLO INTEGER 
    );

-- https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey
-- This was FY20_Outlet data, renamed.

-- COPYING DATA
\set quiet
\copy data.imls_data FROM '/docker-entrypoint-initdb.d/imls-data-2020.csv' DELIMITER ',' CSV HEADER;
\unset quiet