from tkinter.tix import Select
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
    #code = 'AMER3'
    #year_parameter = 2020
    #day_month = '0930'

class DemonstracaoResultadoService():
    def __init__(self, code, year_parameter, day_month):
        self.code = code
        self.year_parameter = year_parameter
        self.day_month = day_month
        self.driver = driver = webdriver.Chrome(ChromeDriverManager().install())


    def get_possible_result_demonstration_year(self):
        self.driver.get(f"https://www.investsite.com.br/demonstracao_resultado.php?cod_negociacao={self.code}")
        element_year_select = self.driver.find_element(By.XPATH, '//*[@id="ano_dem"]')
        print(element_year_select)
        
    def get_demonstracao_resultado(self) -> pd.DataFrame:
        element_final = self._get_html()

        df = pd.read_html(element_final)[0]

        df_rename = df.rename(columns={'Descrição': 'Descricao', 
                                    f'01/07/{self.year_parameter} a 30/09/{self.year_parameter} (R$ mil)': f'01/07/{self.year_parameter}-30/09/{self.year_parameter}', 
                                    '% total': f'01/07/{self.year_parameter}-30/09/{self.year_parameter}-total',
                                    f'01/01/{self.year_parameter} a 30/09/{self.year_parameter} (R$ mil)': f'01/01/{self.year_parameter}-30/09/{self.year_parameter}',
                                    '% total.1': f'01/01/{self.year_parameter}-30/09/{self.year_parameter}-total',
                                    f'01/07/{self.year_parameter - 1} a 30/09/{self.year_parameter - 1} (R$ mil)': f'01/07/{self.year_parameter - 1}-30/09/{self.year_parameter -1 }',
                                    '% total.2': f'01/07/{self.year_parameter - 1}-30/09/{self.year_parameter - 1}-total',
                                    f'01/01/{self.year_parameter - 1} a 30/09/{self.year_parameter - 1} (R$ mil)': f'01/01/{self.year_parameter - 1}-30/09/{self.year_parameter - 1}',
                                    '% total.3': f'01/01/{self.year_parameter - 1}-30/09/{self.year_parameter - 1}-total'})
        
        df_filter = df_rename.dropna(axis=0)
        df_filter = df_filter.fillna(0)
        df_filter = df_filter.replace('-', 0)
        return df_filter

    def _get_html(self) -> str:
        self.driver.get(f"https://www.investsite.com.br/demonstracao_resultado.php?cod_negociacao={self.code}")
        element_year_select = self.driver.find_element(By.XPATH, '//*[@id="ano_dem"]')
        element_year_select.find_element(By.XPATH, f'//*[@value={self.year_parameter}]').click()
        time.sleep(3)
        element_month_select = self.driver.find_element(By.XPATH, '//*[@id="mes_dia_dem"]')
        element_month_select.find_element(By.XPATH, f'//*[@value={self.day_month}]').click()
        time.sleep(3)
        element_central = self.driver.find_element(By.XPATH, '//*[@id="dem_result_empresa"]')
        element = element_central.find_element(By.TAG_NAME, 'table')
        element_final = element.get_attribute('outerHTML').replace(',','.')
        self.driver.quit()
        return element_final


