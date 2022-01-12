from fastapi import FastAPI,Query
from typing import List,Optional
from main import Based_on_BU,reassign_for_not_reported

from pydantic import BaseModel

class bu_input(BaseModel):
    org_name : Optional[str] = Query(None)
    bu_names:Optional[List[str]] = Query(None)
    start_date : Optional[str]= Query(None)
    end_date: Optional[str] = Query(None)

class rm_input(BaseModel):
    org_name: Optional[str] = Query(None)
    reporting_manager: Optional[List[str]] = Query(None)
    start_date: Optional[str] = Query(None)
    end_date: Optional[str] = Query(None)

class employee(BaseModel):
    org_name: Optional[str] = Query(None)
    emp_id: Optional[List[str]] = Query(None)
    start_date: Optional[str] = Query(None)
    end_date: Optional[str] = Query(None)

class re_assignment(BaseModel):
    org_name: Optional[str] = Query(None)
    given_date: Optional[str] = Query(None)


app = FastAPI(
    title = ' Work Space Allocation'
)


@app.post('/Based-on-Business-Unit/')
async def business_unit( item: bu_input ):
    print("\n"*100)
    print(item.org_name,item.bu_names,item.start_date,item.end_date)
    b=Based_on_BU(organization = item.org_name, bu_name = item.bu_names, start_date = item.start_date,
                end_date = item.end_date)
    b.Assign_Dates()
    result=b.Assign_Seats()
    return result

@app.post('/Based-on-Reporting-managers/')
async def Reporting_managers(item: rm_input):
    print("\n" * 100)
    b = Based_on_BU(organization = item.org_name, reporting_managers = item.reporting_manager, start_date = item.start_date,
                    end_date = item.end_date)
    b.Assign_Dates()
    result = b.Assign_Seats()
    return result

@app.post('/Based-on-Employee/')
async def Employee(item:employee):
    print("\n" * 100)
    b = Based_on_BU(organization = item.org_name, employee_ids = item.emp_id, start_date = item.start_date,
                    end_date = item.end_date)
    b.Assign_Dates()
    result = b.Assign_Seats()
    return result

@app.post('/reassignment/')
async def reassign(item:re_assignment):
    print("\n" * 100)
    b = reassign_for_not_reported(organization=item.org_name,given_date=item.given_date)
    result = b.update_now()
    return result
