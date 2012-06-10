from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Text

meta = MetaData()


ip = Table('ip', meta,
    Column('ip_id', Integer, primary_key=True, nullable=False),
    Column('ip', String),
    Column('hits', Integer),
    Column('blocked_date', DateTime),
)

paste = Table('paste', meta,
    Column('paste_id', Integer, primary_key=True, nullable=False),
    Column('private_id', String),
    Column('language', String),
    Column('file_name', Text),
    Column('file_content', Text),
    Column('pub_date', DateTime),
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    ip.create()
    paste.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    paste.drop()
    ip.drop()
