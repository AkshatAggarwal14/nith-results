import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import json

async def find_p_after(p_text: str, table):
    return table.find('p', string=lambda text: text.strip() == p_text).find_next('p').text.strip()

async def getSemesterDetails(semTable, semSummaryTable):
    response = {}

    rows = semTable.find_all('tr')

    semNumber = rows[0].text.strip().split(':')[1].strip()
    response["sem_no"] = semNumber
    
    subData = []

    # rows[1] contains alternate names
    headers = ['sno', 'name', 'code', 'grade', 'points'] 
    
    subRow = rows[2:]
    for subject in subRow:
        subDetails = [td.text.strip() for td in subject.find_all('td')]
        subData.append(dict(zip(headers, subDetails)))
    response["subjects"] = subData

    sgpiDetails = await find_p_after('SGPI', semSummaryTable)
    cgpiDetails = await find_p_after('CGPI', semSummaryTable)
    sgCredits,sgpi = sgpiDetails.split('=')
    sgpi_total, semester_credits = sgCredits.split('/')
    response["sgpi"] = sgpi
    response["sgpi_total"] = sgpi_total
    response["semester_credits"] = semester_credits
    cgCredits,cgpi = cgpiDetails.split('=')
    cgpi_total, total_credits = cgCredits.split('/')
    response["cgpi"] = cgpi
    response["cgpi_total"] = cgpi_total
    response["total_credits"] = total_credits

    return response

async def get_result(rollNo: str):
    try:
        async with aiohttp.ClientSession() as session:
            res = await session.post(f'http://results.nith.ac.in/scheme{rollNo[:2]}/studentresult/result.asp', 
                                     data={'RollNumber': rollNo})
            html = await res.text()
            soup = bs(html, 'html.parser')
            # tables [(1) -> student_detail, (2, 3) -> sem_1, ..., (-1) -> unnecessary details]
            tables = soup.find_all('table', width='100%')
            
            response = {}
            response["roll"] = await find_p_after('ROLL NUMBER', tables[1])
            response["name"] = await find_p_after('STUDENT NAME', tables[1])
            response["father_name"] = await find_p_after('FATHER NAME', tables[1])
            response["cgpi"] = (await find_p_after('CGPI', tables[-2])).split('=')[1]

            semesters = []
            counter = 2
            while counter + 1 < len(tables):
                semesters.append(await getSemesterDetails(tables[counter], tables[counter + 1]))
                counter += 2

            response["semesters"] = semesters

            return {"status": "200", "response": response}
                
    except Exception as err:
        return {"status": "500", "error": str(err)}

# print(asyncio.run(get_result('20bcs017')))

# async def get_ranklist():
#     tasks = []
#     for i in range(1, 91):
#         s = f'20bcs{i:03d}'
#         task = asyncio.ensure_future(get_result(s))
#         tasks.append(task)

#     response = await asyncio.gather(*tasks)
#     return response

# ranklist = []
# for data in asyncio.run(get_ranklist()):
#     try:
#         ranklist.append((data['response']['roll'], data['response']['name'], data['response']['cgpi']))
#     except:
#         pass
# ranklist = sorted(ranklist, key=lambda student: -float(student[2]))

# output = open('temp', 'w')
# for i in range(0, len(ranklist)):
#     print(i + 1, ranklist[i], file=output)
