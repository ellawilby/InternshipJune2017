create table soa (
    zone_ varchar(255) primary key,
    ttl int not NULL default 86400,
    mname varchar(256) not NULL,
    rname varchar(256) not NULL,
    serial char(10) not NULL default regexp_replace(current_date::text, '(....)-(..)-(..)', '\1\2\3') || '01',
    refresh_ int not NULL default 10800,
    retry int not NULL default 3600,
    expire int not NULL default 604800,
    minimum int not NULL default 86400
);

create table a (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL default '@',
    address inet not NULL,
    asn int default NULL,
    country varchar(5) default NULL
);

create table aaaa (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL default '@',
    address inet not NULL
);

create table txt (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL default '@',
    txt_data text not NULL
);

create table spf (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL default '@',
    txt_data text not NULL
);

create table ns (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL default '@',
    nsdname varchar(256) not NULL
);

create table mx (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL default '@',
    preference integer not NULL default 10,
    exchange varchar not NULL
);

create table cname (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL,
    cname varchar(256) not NULL
);

create table srv (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL default '@',
    priority integer not NULL,
    weight integer not NULL,
    port integer not NULL,
    target varchar not NULL
);

create table ptr (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL default '@',
    ptrdname varchar(256) not NULL
);

create table hinfo (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    ttl int default 86400,
    host varchar(256) not NULL default '@',
    cpu varchar(256),
    os varchar(256),
    constraint cpu_os_not_null check (coalesce(cpu, os) is not NULL)
);

create table xfr (
    id bigserial primary key,
    zone_ varchar(256) not NULL references soa on delete cascade,
    client varchar(256)
);
