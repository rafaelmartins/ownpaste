from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime


pre_meta = MetaData()
post_meta = MetaData()
ip = Table('ip', post_meta,
    Column('ip_id', Integer, primary_key=True, nullable=False),
    Column('ip', String(length=45)),
    Column('hits', Integer),
    Column('nonce', String(length=16)),
    Column('blocked_date', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['ip'].columns['nonce'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['ip'].columns['nonce'].drop()
