# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero
# General Public License as published by the Free Software Foundation,
# either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

from config import ConfigClass
from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = ConfigClass.SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class DBConnection:
    def __init__(self):
        self.session = SessionLocal()

    def get_db(self):
        db = self.session
        try:
            yield db
        finally:
            db.close()


class DatasetModel(Base):
    __tablename__ = 'bids_results'
    __table_args__ = {'schema': ConfigClass.SQL_DB_NAME}

    id = Column(Integer, primary_key=True)
    dataset_geid = Column(String())
    created_time = Column(DateTime())
    updated_time = Column(DateTime())
    validate_output = Column(JSON)

    def __init__(self, dataset_geid, created_time, updated_time, validate_output):
        self.dataset_geid = dataset_geid
        self.created_time = created_time
        self.updated_time = updated_time
        self.validate_output = validate_output

    def to_dict(self):
        result = {}
        for field in ['id', 'dataset_geid', 'created_time', 'updated_time', 'validate_output']:
            result[field] = getattr(self, field)
        return result
