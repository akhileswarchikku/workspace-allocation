from fastapi import FastAPI,Query
from typing import List,Optional
from main import Based_on_BU,reassign_for_not_reported

app = FastAPI(
    title = ' Work Space Allocation'
)


@app.post('/Based-on-Business-Unit/')
async def business_unit(org_name : Optional[str] = Query(None), bu_names:Optional[List[str]] = Query(None),start_date : Optional[str]= Query(None),end_date : Optional[str] = Query(None)):
    print("\n"*100)
    print(org_name,bu_names,start_date,end_date)
    b=Based_on_BU(organization = org_name, bu_name = bu_names, start_date = start_date,
                end_date = end_date)
    b.Assign_Dates()
    result=b.Assign_Seats()
    return result

@app.post('/Based-on-Reporting-managers/')
async def Reporting_managers( org_name : Optional[str] = Query(None),reporting_manager : Optional[List[str]] = Query(None),start_date : Optional[str]= Query(None),end_date : Optional[str] = Query(None)):
    print("\n" * 100)
    b = Based_on_BU(organization = org_name, reporting_managers = reporting_manager, start_date = start_date,
                    end_date = end_date)
    b.Assign_Dates()
    result = b.Assign_Seats()
    return result

@app.post('/Based-on-Employee/')
async def Employee(org_name : Optional[str] = Query(None), emp_id : Optional[List[str]] = Query(None),start_date : Optional[str]= Query(None),end_date : Optional[str] = Query(None)):
    print("\n" * 100)
    b = Based_on_BU(organization = org_name, employee_ids = emp_id, start_date = start_date,
                    end_date = end_date)
    b.Assign_Dates()
    result = b.Assign_Seats()
    return result

@app.post('/reassignment/')
async def reassign(org_name : Optional[str] = Query(None),given_date : Optional[str]= Query(None)):
    print("\n" * 100)
    b = reassign_for_not_reported(organization=org_name,given_date=given_date)
    result = b.update_now()
    return result