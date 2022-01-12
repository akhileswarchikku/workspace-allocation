from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, JSON, VARCHAR, DATE, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from psycopg2.errors import UniqueViolation
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import sessionmaker
import datetime
import pandas as pd
import numpy as np
from copy import copy
from random import sample, choice
import datetime
from random import shuffle
import json

engine = create_engine('postgresql://admin_name:password@host_name/database_name') # please Modified this line accordingly
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class organization(Base):
    __tablename__ = 'organization'
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(VARCHAR)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, full_name):
        self.full_name = full_name


class business_unit(Base):
    __tablename__ = 'business_unit'
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(VARCHAR)
    bu_head = Column(VARCHAR)
    org_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, full_name, bu_head, org_id):
        self.full_name = full_name
        self.bu_head = bu_head
        self.org_id = org_id


class employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(VARCHAR)
    emp_code = Column(VARCHAR, unique=True)
    bu_id = Column(Integer, ForeignKey('business_unit.id'), nullable=True)
    is_manager = Column(Boolean)
    manager_id = Column(VARCHAR, nullable=True)
    org_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, full_name, emp_code, bu_id, is_manager, manager_id, org_id, created_at):
        self.full_name = full_name
        self.emp_code = emp_code
        self.bu_id = bu_id
        self.is_manager = is_manager
        self.manager_id = manager_id
        self.org_id = org_id
        self.created_at = created_at


class allocation(Base):
    __tablename__ = 'allocation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_code = Column(VARCHAR, ForeignKey('employee.emp_code'))
    allocation_date = Column(DATE)
    desk_id = Column(VARCHAR)
    day_of_the_week = Column(VARCHAR)
    starting_date = Column(DATE, nullable=False)
    ending_date = Column(DATE, nullable=False)
    attendance = Column(Boolean, nullable=True)
    org_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, emp_code, allocation_date, desk_id, day_of_the_week, starting_date, ending_date, attendance,
                 org_id):
        self.emp_code = emp_code
        self.allocation_date = allocation_date
        self.desk_id = desk_id
        self.day_of_the_week = day_of_the_week
        self.starting_date = starting_date
        self.ending_date = ending_date
        self.attendance = attendance
        self.org_id = org_id


class holidays(Base):
    __tablename__ = 'holidays'
    id = Column(Integer, primary_key=True, autoincrement=True)
    holiday = Column(VARCHAR, nullable=False)
    date = Column(DATE, nullable=False)
    org_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, holiday, date, org_id):
        self.holiday = holiday
        self.date = date
        self.org_id = org_id


class leaves(Base):
    __tablename__ = 'leaves'
    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_code = Column(VARCHAR, ForeignKey('employee.emp_code'), unique=False)
    date = Column(DATE)
    org_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, emp_code, date, org_id):
        self.emp_code = emp_code
        self.date = date
        self.org_id = org_id


class remaining_desk(Base):
    __tablename__ = 'remaining_desk'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bu_id = Column(Integer, ForeignKey('business_unit.id'), nullable=True)
    manager_id = Column(VARCHAR, ForeignKey('employee.emp_code'), nullable=False)
    desk_id = Column(MutableDict.as_mutable(JSONB), nullable=False)
    date = Column(DATE)
    org_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, bu_id, manager_id, desk_id, date, org_id):
        self.bu_id = bu_id
        self.manager_id = manager_id
        self.desk_id = desk_id
        self.date = date
        self.org_id = org_id


class total_desk(Base):
    __tablename__ = 'total_desk'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bu_id = Column(Integer, ForeignKey('business_unit.id'), nullable=True)
    manager_id = Column(VARCHAR, ForeignKey('employee.emp_code'), nullable=False)
    desk_id = Column(MutableDict.as_mutable(JSONB), nullable=False)
    org_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, bu_id, manager_id, desk_id, org_id):
        self.bu_id = bu_id
        self.manager_id = manager_id
        self.desk_id = desk_id
        self.org_id = org_id


Base.metadata.create_all(engine)

#Seats and Dates Allocation

class Based_on_BU():

    def __init__(self, organization, start_date, end_date, bu_name=[], reporting_managers=[], employee_ids=[]):
        self.__engine = create_engine('postgresql://admin_name:password@host_name/database_name') # please Modified this line accordingly
        self.__bu_table = pd.read_sql('business_unit', con=self.__engine)
        self.__holidays_table = pd.read_sql('holidays', con=self.__engine)
        self.__leaves_table = pd.read_sql('leaves', con=self.__engine)
        self.__employee_table = pd.read_sql('employee', con=self.__engine)
        self.__organization_table = pd.read_sql('organization', con=self.__engine)
        self.__remaining_table = pd.read_sql('remaining_desk', con=self.__engine)
        self.__total_desk = pd.read_sql('total_desk', con=self.__engine)
        self.__reporting_managers = reporting_managers
        self.__org_id = organization
        self.__start_date = start_date
        self.__end_date = end_date
        if len(bu_name) == 0:
            self.__bu_name = [i.id for i in session.query(business_unit).all()]
            self.__bu_name.append(np.NaN)
            # print(self.__bu_name)
        else:
            self.__bu_name = [i.id for i in session.query(business_unit).filter((business_unit.full_name.in_(bu_name)))]
        if len(reporting_managers) == 0:
            self.__reporting_managers = list(set([i.manager_id for i in session.query(employee).all()]))
        else:
            self.__reporting_managers = list(set([i.emp_code for i in session.query(employee).filter(
                (employee.emp_code.in_(reporting_managers)) & (employee.is_manager == True))]))
        if len(employee_ids) == 0:
            self.__employee_ids = list(set([i.emp_code for i in session.query(employee).all()]))
        else:
            self.__employee_ids = list(
                set([i.emp_code for i in session.query(employee).filter((employee.emp_code.in_(employee_ids)))]))
            if len(reporting_managers) == 0 and len(bu_name) == 0:
                self.__reporting_managers = []
                self.__bu_name = list(
                    set([i.bu_id for i in session.query(employee).filter((employee.emp_code.in_(employee_ids))).all()]))

    def working_days_from_start_end(self, start, end):
        import random, datetime, calendar
        import dateutil.rrule as rrule
        import dateutil.relativedelta as relativedelta
        holidays = copy(self.__holidays_table[self.__holidays_table['org_id'] == self.__org_id])
        holidays['date'] = holidays['date'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        holidays = holidays['date'].tolist()
        before = datetime.datetime.fromisoformat(start)
        after = datetime.datetime.fromisoformat(end)
        rr = rrule.rrule(rrule.WEEKLY, byweekday=[relativedelta.SU, relativedelta.SA], dtstart=before)
        weekends = rr.between(before, after, inc=True)
        weekends = [x.strftime("%Y-%m-%d %H:%M:%S") for x in weekends]

        sdate = datetime.date(after.year, after.month, after.day)  # start date
        edate = datetime.date(before.year, before.month, before.day)  # end date
        delta = sdate - edate
        all_dates = []
        for i in range(delta.days + 1):
            day = edate + datetime.timedelta(days=i)
            all_dates.append(day.strftime("%Y-%m-%d %H:%M:%S"))
        all_dates = [dates for dates in all_dates if dates not in weekends and dates not in holidays]
        return all_dates

    def check_week_number(self, first_date):
        import datetime
        first = datetime.date(first_date.year, first_date.month, first_date.day).isocalendar()[1]
        return first

    def get_employee_leaves(self, start_date, end_date):
        employee_leaves = copy(self.__leaves_table)
        org = session.query(organization).filter((organization.full_name == self.__org_id)).first().id
        employee_leaves = employee_leaves[employee_leaves['org_id'] == org]
        employee_leaves = pd.merge(self.__employee_table, self.__leaves_table, on='emp_code')[
            ['emp_code', 'bu_id', 'manager_id', 'date']]
        if len(self.__reporting_managers) == 0 and len(self.__bu_name) != 0 and len(self.__employee_ids) != 0:
            employee_leaves = employee_leaves[employee_leaves['bu_id'].isin(self.__bu_name) & (
                employee_leaves['manager_id'].isin(self.__reporting_managers)) & (
                                                  employee_leaves['emp_code'].isin(self.__employee_ids))]
        else:
            employee_leaves = employee_leaves[
                employee_leaves['bu_id'].isin(self.__bu_name) & (employee_leaves['emp_code'].isin(self.__employee_ids))]
        employee_leaves['date'] = employee_leaves['date'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        df = pd.merge(employee_leaves,
                      pd.DataFrame({'date': self.working_days_from_start_end(start=start_date, end=end_date)}),
                      on='date', how='inner')
        if df.empty == True:
            return dict({
                'manager': [],
                'employee': []
            })
        else:
            emp = dict()
            df['emp_code'] = df['emp_code'].astype(str)
            df = pd.merge(self.__employee_table, pd.DataFrame({'emp_code': list(df['emp_code'].values)}), on='emp_code')
            for i in [['manager', True], ['employee', False]]:
                emp[i[0]] = df[df['is_manager'] == i[1]]['emp_code'].values.tolist()
            return emp

    def get_week_name_from_date(self, given_date):
        from datetime import datetime
        from datetime import date
        import calendar
        given_date = str(given_date)
        given_date = datetime.fromisoformat(given_date)
        combination = ()
        my_date = date(given_date.year, given_date.month, given_date.day)
        return calendar.day_name[my_date.weekday()]

    def Assign_Dates(self):
        org = session.query(organization).filter((organization.full_name == self.__org_id)).first().id
        self.dates = self.working_days_from_start_end(self.__start_date, self.__end_date)
        same_weeks = dict()
        for i in self.dates:
            week_number = self.check_week_number(datetime.datetime.fromisoformat(i))
            if week_number in same_weeks.keys():
                same_weeks[week_number].extend([i])
            else:
                same_weeks[week_number] = [i]
        to_assign = copy(self.__employee_table[self.__employee_table['org_id'] == org])
        if len(self.__reporting_managers) == 0 and len(self.__bu_name) != 0 and len(self.__employee_ids) != 0:
            to_assign = to_assign[
                to_assign['bu_id'].isin(self.__bu_name) & (to_assign['emp_code'].isin(self.__employee_ids))]
        else:
            to_assign = to_assign[
                to_assign['bu_id'].isin(self.__bu_name) & (to_assign['manager_id'].isin(self.__reporting_managers)) & (
                    to_assign['emp_code'].isin(self.__employee_ids))]
        to_assign_employee = to_assign[to_assign['is_manager'] == False]['emp_code'].values.tolist()  # Getting Employee
        to_assign_managers = to_assign[to_assign['is_manager'] == True]['emp_code'].values.tolist()  # Getting Managers
        to_assign_managers.extend(to_assign['manager_id'].unique().tolist())
        # to_assign_managers.extend([i.bu_head for i in session.query(business_unit).filter((business_unit.id.in_(to_assign['bu_id'].unique().tolist()))).all()])
        to_assign_employee = list(set(to_assign_employee))
        to_assign_managers = list(set(to_assign_managers))
        leaves_applied = self.get_employee_leaves(self.__start_date, self.__end_date)
        total_dates_allocation = dict()
        for i in leaves_applied:
            if i == 'manager':
                for manager in list(set(to_assign_managers) - set(leaves_applied[i])):
                    for weeks in list(same_weeks.keys()):
                        try:
                            day1, day2, day3 = sample(same_weeks[weeks], 3)
                            while day1 == day2 or day2 == day3 or day3 == day1:
                                day1, day2, day3 = sample(same_weeks[weeks], 3)
                            if manager in total_dates_allocation:
                                total_dates_allocation[manager].extend([day1])
                                total_dates_allocation[manager].extend([day2])
                                total_dates_allocation[manager].extend([day3])
                            else:
                                total_dates_allocation[manager] = [day1]
                                total_dates_allocation[manager].extend([day2])
                                total_dates_allocation[manager].extend([day3])
                        except ValueError:
                            pass
            else:
                for employee in list(set(to_assign_employee) - set(leaves_applied[i])):
                    for weeks in list(same_weeks.keys()):
                        try:
                            day1, day2 = sample(same_weeks[weeks], 2)
                            while day1 == day2:
                                day1, day2 = sample(same_weeks[weeks], 2)
                            if employee in total_dates_allocation:
                                total_dates_allocation[employee].extend([day1])
                                total_dates_allocation[employee].extend([day2])
                            else:
                                total_dates_allocation[employee] = [day1]
                                total_dates_allocation[employee].extend([day2])
                        except ValueError:
                            pass
        for i in leaves_applied:
            if i == 'manager':
                for manager in list(set(leaves_applied[i])):
                    dates = list(set([i.strftime("%Y-%m-%d %H:%M:%S") for i in
                                      self.__leaves_table[self.__leaves_table['emp_code'] == manager][
                                          'date'].to_list()]))
                    for weeks in list(same_weeks.keys()):
                        try:
                            day1, day2, day3 = sample(same_weeks[weeks], 3)
                            while day1 == day2 or day2 == day3 or day3 == day1 or len(
                                    set([day1, day2, day3]).intersection(dates)):
                                day1, day2, day3 = sample(same_weeks[weeks], 3)
                            if manager in total_dates_allocation:
                                total_dates_allocation[manager].extend([day1])
                                total_dates_allocation[manager].extend([day2])
                                total_dates_allocation[manager].extend([day3])
                            else:
                                total_dates_allocation[manager] = [day1]
                                total_dates_allocation[manager].extend([day2])
                                total_dates_allocation[manager].extend([day3])
                        except ValueError:
                            pass
            else:
                for employee in list(set(leaves_applied[i])):
                    dates = list(set([i.strftime("%Y-%m-%d %H:%M:%S") for i in
                                      self.__leaves_table[self.__leaves_table['emp_code'] == manager][
                                          'date'].to_list()]))
                    for weeks in list(same_weeks.keys()):
                        try:
                            day1, day2 = sample(same_weeks[weeks], 2)
                            while day1 == day2 or len(set([day1, day2]).intersection(dates)):
                                day1, day2 = sample(same_weeks[weeks], 2)
                            if employee in total_dates_allocation:
                                total_dates_allocation[employee].extend([day1])
                                total_dates_allocation[employee].extend([day2])
                            else:
                                total_dates_allocation[employee] = [day1]
                                total_dates_allocation[employee].extend([day2])
                        except ValueError:
                            pass
        df = pd.DataFrame(columns=['emp_code', 'allocation_date'])
        for emp in total_dates_allocation:
            df = df.append(pd.DataFrame({
                'emp_code': [emp] * len(total_dates_allocation[emp]),
                'allocation_date': total_dates_allocation[emp]
            })
            )
        df.sort_values(by=['emp_code', 'allocation_date'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        self.total_dates_allocation = df
        self.total_dates_allocation = pd.merge(self.total_dates_allocation, self.__employee_table, on='emp_code')[
            ['emp_code', 'allocation_date', 'bu_id', 'manager_id']]
        self.total_dates_allocation['manager_id'] = np.where(self.total_dates_allocation['manager_id'] == 'V0001',
                                                             self.total_dates_allocation['emp_code'],
                                                             self.total_dates_allocation['manager_id'])
        if len(list(set(self.__employee_ids) & set(to_assign_managers))) != 0:
            return self.total_dates_allocation
        elif len(self.__reporting_managers) == 0 and len(self.__bu_name) != 0 and len(self.__employee_ids) != 0:
            self.total_dates_allocation = self.total_dates_allocation[
                np.logical_not(self.total_dates_allocation['emp_code'].isin(to_assign_managers))]
        return self.total_dates_allocation

    def Assign_Seats(self):
        final_seats_allocated = pd.DataFrame(columns=['emp_code', 'allocation_date', 'bu_id', 'desk_id'])
        overall_remaining_seats = dict()
        seats_remaining_under_buid = dict()
        for buid in self.total_dates_allocation['bu_id'].unique():
            temp_bu_id = self.total_dates_allocation[self.total_dates_allocation['bu_id'] == buid].copy()
            seats_remaining_under_manager_id = dict()
            for manager_id in temp_bu_id['manager_id'].unique():
                temp_df = temp_bu_id[(temp_bu_id['bu_id'] == buid) & (temp_bu_id['manager_id'] == manager_id)].copy()
                seats_remaining_in_date = dict()
                for dates in self.total_dates_allocation['allocation_date'].unique():
                    temp_df_dates = temp_df[temp_df['allocation_date'] == dates].copy()
                    temp_seats_are = session.query(total_desk).filter(
                        (total_desk.bu_id == buid) & (total_desk.manager_id == manager_id)).all()
                    seats_given_in_JS = []
                    for i in temp_seats_are:
                        seats_given_in_JS.extend(i.desk_id['seats'])
                    seats_given_in_JS = list(set(seats_given_in_JS))
                    seats = copy(seats_given_in_JS)
                    shuffle(seats)
                    if temp_df_dates.shape[0] > len(seats):
                        seat_to_assign = seats.extend(['lobby'] * abs(temp_df_dates.shape[0] - len(seats)))
                        temp_df_dates['desk_id'] = seat_to_assign
                        final_seats_allocated = final_seats_allocated.append(temp_df_dates)
                    else:
                        seat_to_assign = seats[0:temp_df_dates.shape[0]]
                        temp_df_dates['desk_id'] = seat_to_assign
                        final_seats_allocated = final_seats_allocated.append(temp_df_dates)
                        seats_remaining = list(set(seats_given_in_JS) - set(seat_to_assign))
                        seats_remaining.sort()
                        seats_remaining_in_date[dates] = seats_remaining
                seats_remaining_under_manager_id[manager_id] = seats_remaining_in_date
            seats_remaining_under_buid[buid] = seats_remaining_under_manager_id
            overall_remaining_seats = seats_remaining_under_buid
            final_seats_allocated = final_seats_allocated[['emp_code', 'allocation_date', 'desk_id']]
            final_seats_allocated.sort_values(by=['emp_code'], inplace=True)
            final_seats_allocated['day_of_the_week'] = final_seats_allocated['allocation_date'].apply(
                self.get_week_name_from_date)
            final_seats_allocated.reset_index(drop=True, inplace=True)
            final_seats_allocated['allocation_date'] = pd.to_datetime(final_seats_allocated['allocation_date'])
            self.final_seats_allocated = final_seats_allocated
            org_id = session.query(organization).filter((organization.full_name == self.__org_id)).first().id
        for i in final_seats_allocated.values:
            try:
                al = allocation(emp_code=i[0], allocation_date=i[1], desk_id=i[2], day_of_the_week=i[3],
                                starting_date=self.__start_date, ending_date=self.__end_date, attendance=None,
                                org_id=org_id)
                session.add(al)
                session.commit()
                session.close()
            except:
                session.rollback()
                session.close()
        for bu_ids in overall_remaining_seats.keys():
            for manager in overall_remaining_seats[bu_ids].keys():
                for dates in overall_remaining_seats[bu_ids][manager].keys():
                    date = datetime.datetime.fromisoformat(dates)
                    seats_in_list = copy(overall_remaining_seats[bu_ids][manager][dates])
                    org_id = session.query(organization).filter((organization.full_name == self.__org_id)).first().id
                    r = remaining_desk(bu_id=bu_ids, manager_id=manager, desk_id={'seats': seats_in_list}, date=date,
                                       org_id=org_id)
                    try:
                        session.add(r)
                        session.commit()
                        session.close()
                    except:
                        session.rollback()
                        session.close()
                dates = set(self.dates) ^ set(list(overall_remaining_seats[bu_ids][manager].keys()))
                for date in dates:
                    seats = session.query(total_desk).filter(
                        (total_desk.bu_id == bu_ids) & (total_desk.manager_id == manager)).first()
                    if seats == None:
                        seats = np.NaN
                    else:
                        seats = seats.desk_id['seats']
                    org_id = session.query(organization).filter((organization.full_name == self.__org_id)).first().id
                    r = remaining_desk(bu_id=bu_ids, manager_id=manager, desk_id={'seats': seats}, date=date,
                                       org_id=org_id)
                    try:
                        session.add(r)
                        session.commit()
                        session.close()
                    except:
                        session.rollback()
                        session.close()
        session.close()
        self.final_seats_allocated = final_seats_allocated
        self.final_seats_allocated = pd.merge(self.final_seats_allocated, self.__employee_table)[
            ['emp_code', 'allocation_date', 'desk_id', 'day_of_the_week', 'manager_id', 'org_id', 'bu_id']]
        self.final_seats_allocated['allocation_date'] = self.final_seats_allocated['allocation_date'].apply(
            lambda x: x.strftime("%Y-%m-%d"))
        org_dict = dict()
        bu_dict = dict()
        for bu_name in self.final_seats_allocated['bu_id'].unique():
            temp_bu_name = self.final_seats_allocated[self.final_seats_allocated['bu_id'] == bu_name]
            manager_dict = dict()
            for manager_id in temp_bu_name['manager_id'].unique():
                temp_manager_name = temp_bu_name[temp_bu_name['manager_id'] == manager_id]
                employee_dict = dict()
                for employee_code in temp_manager_name['emp_code'].unique():
                    temp_employee_name = temp_manager_name[temp_manager_name['emp_code'] == employee_code]
                    temp = temp_employee_name[['allocation_date', 'desk_id', 'day_of_the_week']]
                    temp.columns = ['allocationDate', 'deskID', 'dayOfTheWeek']
                    employee_dict[employee_code] = temp.to_dict('records')
                manager_dict[manager_id] = employee_dict
            bu_dict[bu_name] = manager_dict
        org_dict[self.__org_id] = bu_dict
        self.final_seats_allocated = org_dict
        return self.final_seats_allocated

#Reallocation of Seats

class reassign_for_not_reported():
    def __init__(self, organization, given_date):
        self.__engine = create_engine('postgresql://admin_name:password@host_name/database_name') # please Modified this line accordingly
        self.__bu_table = pd.read_sql('business_unit', con=self.__engine)
        self.__holidays_table = pd.read_sql('holidays', con=self.__engine)
        self.__leaves_table = pd.read_sql('leaves', con=self.__engine)
        self.__employee_table = pd.read_sql('employee', con=self.__engine)
        self.__organization_table = pd.read_sql('organization', con=self.__engine)
        self.__remaining_table = pd.read_sql('remaining_desk', con=self.__engine)
        self.__total_desk = pd.read_sql('total_desk', con=self.__engine)
        self.__org_id = organization
        self.__today = given_date  # datetime.datetime.now().strftime("%Y-%m-%d")
        self.__not_reported = [i.emp_code for i in session.query(allocation).filter(
            (allocation.allocation_date == self.__today) & (allocation.attendance == False)).all()]
        print(self.__not_reported)

    def check_week_number(self, first_date):
        import datetime
        first_date = datetime.datetime.fromisoformat(first_date)
        first = datetime.date(first_date.year, first_date.month, first_date.day).isocalendar()[1]
        return first

    def get_week_name_from_date(self, given_date):
        from datetime import datetime
        from datetime import date
        import calendar
        given_date = str(given_date)
        given_date = datetime.fromisoformat(given_date)
        my_date = date(given_date.year, given_date.month, given_date.day)
        return calendar.day_name[my_date.weekday()]

    def working_days_from_start_end(self, start, end, org_id):
        import random, datetime, calendar
        import dateutil.rrule as rrule
        import dateutil.relativedelta as relativedelta
        holidays = copy(self.__holidays_table[self.__holidays_table['org_id'] == org_id])
        holidays['date'] = holidays['date'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        holidays = holidays['date'].tolist()
        before = datetime.datetime.fromisoformat(start)
        after = datetime.datetime.fromisoformat(end)
        rr = rrule.rrule(rrule.WEEKLY, byweekday=[relativedelta.SU, relativedelta.SA], dtstart=before)
        weekends = rr.between(before, after, inc=True)
        weekends = [x.strftime("%Y-%m-%d %H:%M:%S") for x in weekends]

        sdate = datetime.date(after.year, after.month, after.day)  # start date
        edate = datetime.date(before.year, before.month, before.day)  # end date
        delta = sdate - edate
        all_dates = []
        for i in range(delta.days + 1):
            day = edate + datetime.timedelta(days=i)
            all_dates.append(day.strftime("%Y-%m-%d %H:%M:%S"))
        all_dates = [dates for dates in all_dates if dates not in weekends and dates not in holidays]
        return all_dates

    def update_now(self):
        buId = []
        managerId = []
        orgID = []
        employeeID = []
        previousDate = []
        previousDeskId = []
        updatedDate = []
        updatedDeskId = []
        for employeeid in self.__not_reported:
            buid = session.query(employee).filter((employee.emp_code == employeeid)).first().bu_id
            manager = session.query(employee).filter((employee.emp_code == employeeid)).first().manager_id
            check_manager = session.query(employee).filter((employee.emp_code == employeeid)).first()
            if check_manager.is_manager:
                manager = check_manager.emp_code
            start_date = session.query(allocation).filter((allocation.allocation_date == self.__today) & (
                        allocation.emp_code == employeeid)).first().starting_date.strftime("%Y-%m-%d")
            end_date = session.query(allocation).filter((allocation.allocation_date == self.__today) & (
                        allocation.emp_code == employeeid)).first().ending_date.strftime("%Y-%m-%d")
            org_id = session.query(allocation).filter(
                (allocation.allocation_date == self.__today) & (allocation.emp_code == employeeid)).first().org_id
            dates = [datetime.datetime.fromisoformat(i).strftime("%Y-%m-%d") for i in
                     self.working_days_from_start_end(self.__today, end_date, org_id)]
            assigned_dates = [i.allocation_date.strftime("%Y-%m-%d") for i in
                              session.query(allocation).filter((allocation.emp_code == employeeid)).all()]
            org_id = session.query(organization).filter((organization.full_name == self.__org_id)).first().id
            leave_dates = [i.date.strftime("%Y-%m-%d") for i in
                           session.query(leaves).filter((leaves.emp_code == employeeid)).all()]
            remaining_dates = list(set(leave_dates) ^ set(dates) ^ set(assigned_dates))
            remaining_dates = [date for date in remaining_dates if date in dates]
            remaining_dates.sort()
            oldSeat = session.query(allocation).filter(
                (allocation.emp_code == employeeid) & (allocation.allocation_date == self.__today)).first().desk_id
            seat = None
            for date in remaining_dates:
                desk_ids = session.query(remaining_desk).filter(
                    (remaining_desk.bu_id == buid) & (remaining_desk.manager_id == manager) & (
                                remaining_desk.date == date)).first()
                if desk_ids != None:
                    seats_available = copy(desk_ids.desk_id['seats'])
                    seat = choice(seats_available)
                    seats_available = list(set(seats_available) ^ set([seat]))
                    dic = dict()
                    dic["seats"] = seats_available
                    session.query(remaining_desk).filter((remaining_desk.bu_id == buid) &
                                                         (remaining_desk.manager_id == manager) &
                                                         (remaining_desk.date == date)).update(
                        {remaining_desk.desk_id: dic})
                    session.commit()
                    session.close()
                    break
            try:
                if seat == None:
                    check = session.query(allocation).filter(
                        (allocation.emp_code == employeeid) & (allocation.allocation_date == self.__today)).first()
                    if check != None:
                        buId.append(buid)
                        managerId.append(manager)
                        orgID.append(org_id)
                        employeeID.append(employeeid)
                        previousDate.append(self.__today)
                        previousDeskId.append(oldSeat)
                        updatedDate.append(remaining_dates[0])
                        updatedDeskId.append(np.NaN)
                        session.query(allocation).filter((allocation.emp_code == employeeid) &
                                                         (allocation.allocation_date == self.__today)
                                                         ).update({allocation.allocation_date: remaining_dates[0],
                                                                   allocation.desk_id: None,
                                                                   allocation.day_of_the_week: self.get_week_name_from_date(
                                                                       remaining_dates[0]),
                                                                   allocation.attendance: None,
                                                                   allocation.modified_date: datetime.datetime.utcnow()
                                                                   })
                        session.commit()
                        session.close()
                    else:
                        buId.append(buid)
                        managerId.append(manager)
                        orgID.append(org_id)
                        employeeID.append(employeeid)
                        previousDate.append(self.__today)
                        previousDeskId.append(oldSeat)
                        updatedDate.append(remaining_dates[0])
                        updatedDeskId.append(np.NaN)
                        new_allocation = allocation(emp_code=employeeid,
                                                    allocation_date=remaining_dates[0],
                                                    day_of_the_week=self.get_week_name_from_date(remaining_dates[0]),
                                                    desk_id=seat, starting_date=start_date,
                                                    ending_date=end_date,
                                                    attendance=None,
                                                    org_id=org_id
                                                    )
                        session.add(new_allocation)
                        session.commit()
                        session.close()
                else:
                    check = session.query(allocation).filter(
                        (allocation.emp_code == employeeid) & (allocation.allocation_date == self.__today)).first()
                    if check != None:
                        buId.append(buid)
                        managerId.append(manager)
                        employeeID.append(employeeid)
                        orgID.append(org_id)
                        previousDate.append(self.__today)
                        previousDeskId.append(oldSeat)
                        updatedDate.append(date)
                        updatedDeskId.append(seat)
                        session.query(allocation).filter((allocation.emp_code == employeeid) &
                                                         (allocation.allocation_date == self.__today)
                                                         ).update({allocation.allocation_date: date,
                                                                   allocation.desk_id: seat,
                                                                   allocation.day_of_the_week: self.get_week_name_from_date(
                                                                       date),
                                                                   allocation.attendance: None,
                                                                   allocation.modified_date: datetime.datetime.utcnow()
                                                                   })
                        session.commit()
                        session.close()
                    else:
                        buId.append(buid)
                        managerId.append(manager)
                        orgID.append(org_id)
                        previousDate.append(self.__today)
                        previousDeskId.append(oldSeat)
                        updatedDate.append(date)
                        updatedDeskId.append(seat)
                        employeeID.append(employeeid)
                        new_allocation = allocation(emp_code=employeeid,
                                                    allocation_date=date,
                                                    day_of_the_week=self.get_week_name_from_date(date),
                                                    desk_id=seat, starting_date=start_date,
                                                    ending_date=end_date,
                                                    attendance=None,
                                                    org_id=org_id
                                                    )
                        session.add(new_allocation)
                        session.commit()
                        session.close()
            except:
                session.rollback()
                session.close()
        updated = pd.DataFrame(
            {
                'orgId': orgID,
                'buId': buId,
                'managerId': managerId,
                'employeeId': employeeID,
                'previousDate': previousDate,
                'previousDeskId': previousDeskId,
                'updatedDate': updatedDate,
                'updatedDeskId': updatedDeskId
            }
        )
        updated['orgId']=updated['orgId'].astype(int) 
        org_dict = dict()
        for org_id in updated['orgId'].unique():
            org_name=session.query(organization).filter((organization.id == int(org_id))).first().full_name
            bu_dict = dict()
            for bu_name in updated[updated['orgId']==org_id]['buId'].unique():
                temp_bu_name = updated[updated['buId'] == bu_name ]
                manager_dict = dict()
                for manager_id in temp_bu_name['managerId'].unique():
                    temp_manager_name = temp_bu_name[temp_bu_name['managerId'] == manager_id]
                    employee_dict = dict()
                    for employee_code in temp_manager_name['employeeID'].unique():
                        temp_employee_name = temp_manager_name[temp_manager_name['employeeID'] == employee_code]
                        temp = temp_employee_name[['previousDate', 'previousDeskId', 'updatedDate', 'updatedDeskId']]
                        employee_dict[employee_code] = temp.to_dict('records')
                    manager_dict[manager_id] = employee_dict
                bu_dict[float(bu_name)] = manager_dict
            org_dict[org_name] = bu_dict
        return org_dict 
