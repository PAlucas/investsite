from demonstracao_resultado_service import DemonstracaoResultadoService
import pandas as pd

dados : pd.DataFrame = DemonstracaoResultadoService('PETR3', 2021, '0930').get_possible_result_demonstration_year()

print(dados)

