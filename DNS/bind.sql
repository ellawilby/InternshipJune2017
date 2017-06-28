--
-- Database schema
--

create table soa (
    zone_ varchar(255) primary key,                -- zone name
    ttl int not NULL default '1 day',        -- time to live
    mname varchar(256) not NULL,                  -- the original or primary source of data for this zone
    rname varchar(256) not NULL,                  -- responsible person's email
    serial char(10) not NULL default              -- number of the original copy of the zone
         regexp_replace(current_date::text, '(....)-(..)-(..)', '\1\2\3') || '01', -- generate serial from date
    refresh_ int not NULL default '3 hours',  -- time interval before the zone should be refreshed
    retry int not NULL default '1 hour',     -- time interval that should elapse before a failed refresh should be retried
    expire int not NULL default '1 week',    -- time interval that can elapse before the zone is no longer authoritative
    minimum int not NULL default '1 day'     -- minimum TTL field that should be exported with any RR from this zone
);

-- INSERT INTO "tempSchema".soa(zone_, ttl, mname, rname, serial, refresh_, retry, expire, minimum) VALUES ('.NET', '15 min'::interval, 'a.gtld-servers.net.', 'nstld.verisign-grs.com.', '1487827201', '30 min'::interval, '15 min'::interval, '1 week'::interval, '1 day'::interval);


create table a (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,    -- zone must exists in soa table
    ttl int default NULL,
    host varchar(256) not NULL default '@',
    address inet not NULL
);

create table aaaa (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default NULL,
    host varchar(256) not NULL default '@',
    address inet not NULL
);

create table txt (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default NULL,
    host varchar(256) not NULL default '@',
    txt_data text not NULL
);

create table spf (
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default NULL,
    host varchar(256) not NULL default '@',
    txt_data text not NULL
);

create table ns (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default NULL,
    host varchar(256) not NULL default '@',
    nsdname varchar(256) not NULL
);

-- INSERT INTO "tempSchema".ns(zone_, ttl, host, nsdname) VALUES ('.NET', '15 min'::interval, 'TOOLS24', 'NS.CHECKDOMAIN.DE.');

create table mx (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default NULL,
    host varchar(256) not NULL default '@',
    preference integer not NULL default 10,
    exchange varchar not NULL
);

create table cname (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default NULL,
    host varchar(256) not NULL,
    cname varchar(256) not NULL
);

create table srv (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default NULL,
    host varchar(256) not NULL default '@',
    priority integer not NULL,
    weight integer not NULL,
    port integer not NULL,
    target varchar not NULL
);

create table ptr (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default NULL,
    host varchar(256) not NULL default '@',
    ptrdname varchar(256) not NULL
);

create table hinfo (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default NULL,
    host varchar(256) not NULL default '@',
    cpu varchar(256),
    os varchar(256),
    constraint cpu_os_not_null check (coalesce(cpu, os) is not NULL) -- at least one of `cpu', `os' must be not null
);

create table xfr (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    client varchar(256)
);

-- view returning records of all types except `NS' and `SOA'
create view d_records as
    select 
        host,
        case when a.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from a.ttl) end as ttl, -- if `ttl' in table `a' is not NULL select its value. Select value of `soa.ttl' in other case.
        'A' as type,
        NULL as priority,
        host(address) as data, 
        soa.zone
        from a, soa where soa.zone = a.zone
    union
    select
        host,
        case when aaaa.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from aaaa.ttl) end as ttl,
        'AAAA' as type,
        NULL as priority,
        host(address) as data,
        soa.zone
        from aaaa, soa where soa.zone = aaaa.zone
    union
    select
        host,
        case when mx.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from mx.ttl) end as ttl,
        'MX' as type,
        preference::text as priority,
        exchange as data,
        soa.zone
        from mx, soa where soa.zone = mx.zone
    union
    select/home/ella/bindproc/bind-parser-master
        host,
        case when txt.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from txt.ttl) end as ttl,
        'TXT' as type,
        NULL as priority,
        '"' || txt_data || '"' as data, -- add double quotes to text data cause it can contain whitespaces
        soa.zone
        from txt, soa where soa.zone = txt.zone
    union
    select
        host,
        case when spf.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from spf.ttl) end as ttl,
        'SPF' as type,
        NULL as priority,
        '"' || txt_data || '"' as data,
        soa.zone
        from spf, soa where soa.zone = spf.zone
    union
    select
        host,
        case when srv.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from srv.ttl) end as ttl,
        'SRV' as type,
        priority::text as priority,
        weight::text || ' ' || port::text || ' ' || target::text as data, -- concatenate fields as DLZ driver do not expect so much elements in tuple returned from postgres
        soa.zone
        from srv, soa where soa.zone = srv.zone
    union
    select 
        host,
        case when cname.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from cname.ttl) end as ttl,
        'CNAME' as type,
        NULL as priority,
        cname as data,
        soa.zone
        from cname, soa where soa.zone = cname.zone
    union
    select 
        host,
        case when ptr.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from ptr.ttl) end as ttl,
        'PTR' as type,
        NULL as priority,
        ptrdname as data,
        soa.zone
        from ptr, soa where soa.zone = ptr.zone
    union
    select 
        host,
        case when hinfo.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from hinfo.ttl) end as ttl,
        'HINFO' as type,
        NULL as priority,
        cpu || ' ' || os as data,
        soa.zone
        from hinfo, soa where soa.zone = hinfo.zone
;

-- view returning `NS' and `SOA' record types
create view ns_records as
    select
        case when ns.ttl is NULL then extract('epoch' from soa.ttl) else extract('epoch' from ns.ttl) end as ttl,
        'NS' as type,
        NULL as priority,
        nsdname as data,
        NULL as resp_person,
        NULL as serial,
        NULL as refresh,
        NULL as retry,
        NULL as expire,
        NULL as minimum,
        soa.zone,
        host
        from ns, soa where soa.zone = ns.zone
    union
    select
        extract('epoch' from ttl) as ttl,
        'SOA' as type,
        NULL as priority,
        mname as data,
        rname as resp_person,
        serial,
        extract('epoch' from refresh),
        extract('epoch' from retry),
        extract('epoch' from expire),
        extract('epoch' from minimum),
        zone,
        '@' as host
        from soa
;

-- view returning all types of records
create view all_records as
    select
        ttl,
        type,
        host as host,
        priority,
        data,
        NULL as resp_person,
        NULL as serial,
        NULL as refresh,
        NULL as retry,
        NULL as expire,
        NULL as minimum,
        zone
        from d_records
    union
    select
        ttl,
        type,
        host,
        priority,
        data,
        resp_person,
        serial,
        refresh,
        retry,
        expire,
        minimum,
        zone
        from ns_records
;

