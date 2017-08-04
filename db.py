from conf import *
from datetime import datetime
from sqlalchemy import MetaData, Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = MetaData()


class Internalnetworkdata(Base):
    __tablename__ = 'internalnetworkdata'
    id = Column(Integer, primary_key=True)
    iteration_number = Column(Integer, nullable=True)
    start_time = Column('start_time',DateTime, default=datetime.utcnow)
    file_size = Column('file_size_bytes', Integer, nullable=True)
    file_count = Column('file_count',Integer, nullable=True)
    transferred_bytes = Column(Integer, nullable=True)
    completion_time = Column('completion_time_seconds',Float, nullable=True)
    packet_loss = Column(Float, nullable=True)
    throughput = Column('throughput_mbps', Float(30), nullable=True)

    def __init__(self,iteration_number, file_size, file_count, completion_time, transferred_bytes, packet_loss, throughput):
        self.iteration_number = iteration_number
        self.file_size = file_size
        self.file_count = file_count
        self.transferred_bytes = transferred_bytes
        self.completion_time = completion_time,
        self.packet_loss = packet_loss
        self.throughput = throughput


# DB connection format: "engine://user:password@host:port/database"
Ignition = create_engine("mysql+pymysql://%s:%s@%s:3306/%s" % (db_user, db_password, db_host, db_name))

# Create DB schema
Base.metadata.create_all(Ignition)
