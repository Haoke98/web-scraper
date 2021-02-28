# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import math
import os
import time

import numpy as np
import requests
import xlwt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def print_hi(res: requests.api):
    # Use a breakpoint in the code line below to debug your script.
    # url = "https://www.zhipin.com/job_detail/7dd71bd45685ab371nV73921FFRT.html?ka=search_list_jname_1_blank&lid=4RagVLoCKMT.search.1"
    res = requests
    print(res.content)
    with open("res.html", "wb") as f:
        f.write(res.content)
    # print(res.text)


def test(chrome_exe_path: str, url: str):
    chrome_option = Options()
    chrome_option.add_argument("--disable-extensions")
    # chrome_option.add_argument("headless")
    chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # browser = webdriver.Chrome(executable_path=chrome_exe_path, chrome_options=chrome_option)
    browser = webdriver.Chrome(executable_path=chrome_exe_path)
    browser.get("https://www.baidu.com")
    browser.implicitly_wait(10)
    _web_element = browser.find_element_by_class_name('salary')
    print(_web_element.text)


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return 0


class BossJob:
    browser = None
    domain = "https://www.zhipin.com"
    query = "c100010000-p120106"
    detailXls = "%s.xls" % query
    sheetPageIndex = "sheet1"
    sheetDetailPagesUrl = "sheet2"
    sheetDetails = "sheet3"
    baseUrl = "%s/%s/" % (domain, query)
    settings = dict({'query':
                         "c100010000-p120106",
                     "searchResPageCount": 7,
                     "detailPageCount": 201,
                     "completedSearchResPages": [1,
                                                 2],
                     "detailPageUrls": {
                         "https://www.zhipin.com/job_detail/9b75676759ce35611nVz2d27ElpV.html": {"fromPageIndex": 2,
                                                                                                 "isComplete": False},
                         "https://www.zhipin.com/job_detail/431d75532bbc0f281nV82dW7FVVT.html": {"fromPageIndex": 2,
                                                                                                 "isComplete": False},
                     },
                     }
                    )

    def __init__(self, query: str):
        self.query = query
        self.__loadSettings__()
        print(self.settings)
        self.baseUrl = "%s/%s/" % (self.domain, query)
        self.detailXls = "%s.xlsx" % query

    def __browserInitializer__(self):
        if self.browser is None:
            chrome_option = Options()
            # chrome_option.add_argument("--disable-extensions")
            # chrome_option.add_argument("headless")
            # chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.browser = webdriver.Chrome(options=chrome_option)
        self.browser.implicitly_wait(10)

    def __getNpyFileName__(self) -> str:
        return "%s.npy" % self.query

    def __saveSettings__(self):
        np.save(self.__getNpyFileName__(), self.settings)

    def __loadSettings__(self):
        if os.path.exists(self.__getNpyFileName__()):
            self.settings = np.load(self.__getNpyFileName__(), allow_pickle=True).item()
        else:
            self.settings = {
                "query": self.query,
                "searchResPageCount": None,
                "detailPageCount": None,
                "completedSearchResPages": [],
                "detailPageUrls": {}
            }

    def __getCurrQueryConfig__(self) -> dict:
        return dict(self.settings)

    def __checkCurrPageIsCompleted__(self, pageIndex: int) -> bool:
        self.__getCurrQueryConfig__().setdefault("completedSearchResPages", [])
        pageIndexList = self.__getCurrQueryConfig__().get("completedSearchResPages")
        if pageIndex in pageIndexList:
            return True
        else:
            return False

    def __getCurrQueryCompletedSearchResPagesList__(self) -> list:
        return self.__getCurrQueryConfig__().get("completedSearchResPages")

    def __setCompletePageIndex__(self, pageIndex):
        self.__getCurrQueryCompletedSearchResPagesList__().append(pageIndex)
        self.__saveSettings__()

    def __getDetailPageUrlsDic__(self) -> dict:
        key = "detailPageUrls"
        dic = self.__getCurrQueryConfig__()
        dic.setdefault(key, {})
        return dic.get(key)

    def __saveDetailPagesUrl__(self, urls: list, pageIndex: int):
        detailPageUrlsDic = self.__getDetailPageUrlsDic__()
        for i in urls:
            detailPageUrlsDic.setdefault(i, {"fromPageIndex": pageIndex, "isComplete": False})
        self.__saveSettings__()

    def getDetailPagesCount(self) -> int:
        searchResPageCount = self.__getCurrQueryConfig__().get("searchResPageCount", None)
        if searchResPageCount is None:
            self.__browserInitializer__()
            self.browser.get(self.baseUrl)
            job_tab_div = self.browser.find_element_by_class_name('job-tab')
            detailPageCount = job_tab_div.get_attribute('data-rescount')
            searchResPageCount = math.ceil((int(detailPageCount) / 30))
            self.settings["searchResPageCount"] = searchResPageCount
            self.settings["detailPageCount"] = detailPageCount
            self.__saveSettings__()
        return searchResPageCount

    def getAllDetailPageUrl(self):
        for pageIndex in range(1, 1 + bossJob.getDetailPagesCount()):
            if self.__checkCurrPageIsCompleted__(pageIndex):
                pass
            else:
                url = "%s?page=%d&ka=page-%d" % (self.baseUrl, pageIndex, pageIndex)
                url_list = self.__getDetailPageUrl__(url)
                print("获取%d页成功" % pageIndex, url_list)
                self.__saveDetailPagesUrl__(url_list, pageIndex)
                self.__setCompletePageIndex__(pageIndex)
                time.sleep(3)

    def __getDetailPageUrl__(self, url: str) -> list:
        self.__browserInitializer__()
        self.browser.get(url)

        _web_elements = self.browser.find_elements_by_class_name('primary-box')

        detail_page_url_list = []
        for index, web_element in enumerate(_web_elements):
            href = "https://www.zhipin.com" + web_element.get_attribute('href')
            detail_page_url_list.append(href)
        return detail_page_url_list

    def getDetails(self):

        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('sheet1')
        i = 0
        worksheet.write(i, 0, "职位名称")
        worksheet.write(i, 1, "职位薪水")
        worksheet.write(i, 2, "职位所在城市")
        worksheet.write(i, 3, "职位经验需求")
        worksheet.write(i, 4, "职位学历需求")
        worksheet.write(i, 5, "职位描述")
        worksheet.write(i, 6, "公司名称")
        worksheet.write(i, 7, "公司登记")
        worksheet.write(i, 8, "公司规模")
        worksheet.write(i, 9, "公司所属行业")
        worksheet.write(i, 10, "来自页面的url")
        detailPagesDic = self.__getDetailPageUrlsDic__()
        for detail_url in detailPagesDic.keys():
            i += 1
            if i > 3000:
                break
            detailPage = detailPagesDic.get(detail_url)
            if detailPage.get("isComplete"):
                print("该页面：%s 已经爬取过。" % detail_url)
                self.__writeByDetailPageDict__(worksheet, i, detailPage, detail_url)
                continue
            else:
                self.__browserInitializer__()
                self.browser.get(detail_url)
                info_primary_div = self.browser.find_element_by_class_name('info-primary')
                job_name_div = info_primary_div.find_element_by_class_name('name')
                job_title = job_name_div.find_element_by_tag_name('h1').text
                job_salary = job_name_div.find_element_by_tag_name('span').text
                city_element = info_primary_div.find_element_by_class_name('text-city')
                city = city_element.text
                p_element = info_primary_div.find_element_by_tag_name('p')
                experiment_degree = str(p_element.text).replace(city, '')
                experiment = experiment_degree[0:4]
                degree = experiment_degree[4:]
                job_description = self.browser.find_element_by_class_name('text').text
                side_company_div = self.browser.find_element_by_class_name('sider-company')
                company_info_div = side_company_div.find_element_by_class_name('company-info')
                a_tags = company_info_div.find_elements_by_tag_name('a')
                second_a_tag = a_tags[1]
                company_name = second_a_tag.text
                company_name = str(company_name).replace(" ", "")
                p_tags = side_company_div.find_elements_by_tag_name('p')
                stage_p_tag = p_tags[1]
                company_stage = stage_p_tag.text
                scale_p_tag = p_tags[2]
                company_scale = scale_p_tag.text
                industry_p_tag = p_tags[3]
                company_industry = industry_p_tag.text
                print(job_title, job_salary, city, experiment, degree, job_description, company_name, "|||",
                      company_stage,
                      "|||", company_scale, "|||", company_industry)

                detailPage["job_title"] = job_title
                detailPage["job_salary"] = job_salary
                detailPage["city"] = city
                detailPage["experiment"] = experiment
                detailPage["degree"] = degree
                detailPage["job_description"] = job_description
                detailPage["company_name"] = company_name
                detailPage["company_stage"] = company_stage
                detailPage["company_scale"] = company_scale
                detailPage["company_industry"] = company_industry

                self.__writeByDetailPageDict__(worksheet, i, detailPage, detail_url)

                workbook.save(self.detailXls)
                detailPage["isComplete"] = True
                self.__saveSettings__()
                # print(web_element.text)
                # print(len(detail_page_url_list))
                # print(_web_element.text)

    def __writeByDetailPageDict__(self, worksheet: xlwt.Worksheet, rowIndex: int, detailPage: dict, detailUrl: str):
        i = rowIndex
        worksheet.write(i, 0, detailPage["job_title"])
        worksheet.write(i, 1, detailPage["job_salary"])
        worksheet.write(i, 2, detailPage["city"])
        worksheet.write(i, 3, detailPage["experiment"])
        worksheet.write(i, 4, detailPage["degree"])
        worksheet.write(i, 5, detailPage["job_description"])
        worksheet.write(i, 6, detailPage["company_name"])
        worksheet.write(i, 7, detailPage["company_stage"])
        worksheet.write(i, 8, detailPage["company_scale"])
        worksheet.write(i, 9, detailPage["company_industry"])
        worksheet.write(i, 10, detailUrl)

    # def check_detail_url(self, detail_url: str):
    #     workbook = xlrd.open_workbook_xls(self.detailXls)
    #     sheet = workbook.get_sheet(0)
    #     print(sheet.name)
    #     for row_index in range(sheet.nrows):
    #         url = sheet.cell_value(10, row_index)
    #         res = url == detail_url
    #         print(url, detail_url, res)
    #         if res:
    #             # 如果是一样就返回
    #             return False
    #         else:
    #             continue
    #     return True
    # # def __init_xlsx(self):
    #     writer = pd.ExcelWriter(self.detailXls)
    #     dicForSheet1 = {"pageIndex": [], }
    #     dicForSheet2 = {"url": [], "complete": []}
    #     dicForSheet3 = {}
    #     dicts = [dicForSheet1, dicForSheet2, dicForSheet3]
    #     sheets = ["sheet1", "sheet2", "sheet3"]
    #     for i in range(0, len(dicts)):
    #         df = pd.DataFrame(dicts[i])
    #         df.to_excel(writer, sheet_name=sheets[i], index=False)
    #     writer.save()
    #     writer.close()

    # def __getDateFrameFromSheet__(self, sheetName: str):
    #     if os.path.exists(self.detailXls):
    #         data = pd.read_excel(self.detailXls, sheetName)
    #         return pd.DataFrame(data)
    #     else:
    #         self.__init_xlsx()
    #         return self.__getDateFrameFromSheet__(sheetName)

    # def __getDicFromSheet__(self, sheetName: str):
    #     df = self.__getDateFrameFromSheet__(sheetName)
    #     return dict(df.to_dict())

    # def saveOtherSheet(self, currSheetName: str, currSheetData: dict):
    #     sheets = [self.sheetDetailPagesUrl, self.sheetPageIndex, self.sheetDetails]
    #     sheets.remove(currSheetName)
    #     dataList = []
    #     for sheetName in sheets:
    #         dataList.append(pd.read_excel(self.detailXls, sheet_name=sheetName))
    #     writer = pd.ExcelWriter(self.detailXls)
    #     for i, sheetName in enumerate(sheets):
    #         data = pd.DataFrame(dataList[i])
    #         data.to_excel(writer, sheet_name=sheetName, index=False)
    #     df = pd.DataFrame(currSheetData)
    #     df.to_excel(writer, sheet_name=currSheetName, index=False)
    #     writer.save()
    #     writer.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bossJob = BossJob("c100010000-p120106")
    print(bossJob.baseUrl, bossJob.detailXls)
    # bossJob.getDetailPagesCount()
    # a = {"sadam": " a boy ", "age": 22, 1: "kalbim"}
    # a.setdefault("x", {"b": "inner dict."})
    # test_npy_file = "test.npy"
    # np.save(test_npy_file, a)
    # if os.path.exists(test_npy_file):
    #     a_loaded = np.load(test_npy_file,
    #                        allow_pickle=True).item()
    #     print(a_loaded)
    bossJob.getAllDetailPageUrl()
    bossJob.getDetails()
    # for i in range(0, 100):
    #     print(i)
    #     time.sleep(3)
    # testXlsxFileName = "test2.xlsx"
    # if os.path.exists(testXlsxFileName):
    #     data = pd.read_excel(testXlsxFileName, sheet_name="sheet2")
    #     data = pd.DataFrame(data)
    #     x = data.to_dict()
    #     # data.to_json()
    #     print(x)
    #     # data.pageIndex.append(10)
    #
    #     print(data)

    #     print(data[data.pageIndex == 6].complete == False)
    #     x = 5
    #     if data[data.pageIndex == x].empty:
    #         print("该项是没有的", x)
    #     else:
    #         print("该项目是有的", x)
    #
    #     for pi in data.pageIndex:
    #         # pi += 1
    #         if data[data.pageIndex == pi].complete.bool():
    #             print("这是True:", pi)
    #         else:
    #             print("这是False", pi)
    #     print(data[data.complete == False])
    #
    #     # data = pd.read_excel(bossJob.detailXls, sheet_name="sheet2")
    #     # print(data)
    #     # print(data[data.职位所在城市 == '南京'])
    # dic = {
    #     "detailPageUrl": [
    #         "https://www.zhipin.com/job_detail/9b75676759ce35611nVz2d27ElpV.html",
    #         "https://www.zhipin.com/job_detail/431d75532bbc0f281nV82dW7FVVT.html",
    #         2, 3, 4, 5
    #     ],
    #     "complete": [True, False, True, False, True, False]
    #
    # }
    # writer = pd.ExcelWriter(testXlsxFileName)
    # df = pd.DataFrame(dic)
    # df.to_excel(writer, sheet_name='sheet2', index=False)
    # dic = {
    #     "pageIndex": [0, 1, 2, 3, 4, 5],
    #     "complete": [True, False, True, False, True, False]
    #
    # }
    # df = pd.DataFrame(dic)
    # df.to_excel(writer, sheet_name='sheet1', index=False)
    # writer.save()
    # x = 10
    # for i in range(0, x):
    #     print(i)
    #     x = 5
    # bossJob.getAllDetailPageUrl()
    # bossJob.getDetails()
    # dic = {'x': 30}
    # a = [0, 1]

    # getAllDetailPageUrl()
    # url = "https://www.zhipin.com/c100010000-p120106/"
    # test2(url)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
