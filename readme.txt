Steps to follow to Run the workspace allocation FASTAPI

Please connect the create engine based on your username and password in line 19, line 165 and line 502 in main.py
create_engine('postgresql://admin_name:password@host_name/db_name')

step 1) Open database folder load 'Workspace.sql' in Postgres using pgadmin
step 2) cd 3_Fast_API
step 3) pip install -r requirements.txt
step 4) cd Fastapi_work_allocation
step 5) run this command 'uvicorn app:app --reload'

