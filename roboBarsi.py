from yahoo_fin import stock_info as si
import pandas as pd
import yfinance as yf
from datetime import datetime
import sys
import os



def get_p_vpa(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    # Obter o preço atual da ação
    current_price = info.get('currentPrice')

    # Obter o patrimônio líquido total
    try:
        total_equity = stock.balance_sheet.loc['Total Stockholder Equity'].iloc[0]
    except:
        return 0
    # Obter o número de ações em circulação
    shares_outstanding = info.get('sharesOutstanding')

    if total_equity and shares_outstanding:
        # Calcular o VPA
        vpa = total_equity / shares_outstanding

        # Calcular o P/VPA
        p_vpa = current_price / vpa
        return p_vpa
    else:
        return 0
    
def get_company_age(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    # Obter a data de fundação
    founded_year = info.get('founded')
    if founded_year:
        current_year = datetime.now().year
        company_age = current_year - founded_year
        return company_age
    else:
        return 0


def calculate_roe(ticker):
    dados = yf.Ticker(ticker).info
    try:
        lucro_liquido = dados['totalRevenue'] - dados['totalExpenses']  # Simplificação, verifique a documentação do yfinance para obter os valores exatos
        patrimonio_liquido = dados['totalStockholdersEquity',1]
        roe = lucro_liquido / patrimonio_liquido
        pass
    except:
        return 0
    return roe
# Função para calcular ROIC
def calculate_roic(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials
    balance_sheet = stock.balance_sheet

    # Obter lucro operacional e capital investido
    try:
        ebit = financials.loc['Ebit'].iloc[0]
        total_assets = balance_sheet.loc['Total Assets'].iloc[0]
        current_liabilities = balance_sheet.loc['Total Current Liabilities'].iloc[0]
    except:
        return 0
    # Calcular NOPAT (Net Operating Profit After Taxes)
    tax_rate = 0.21  # Supondo uma taxa de imposto de 21%
    nopat = ebit * (1 - tax_rate)

    # Calcular capital investido
    capital_invested = total_assets - current_liabilities

    # Calcular ROIC
    roic = nopat / capital_invested
    return roic


def c_cagr(ticker, start_date, end_date):
    # Obter os dados históricos
    df = yf.download(ticker, start=start_date, end=end_date)

    # Calcular o CAGR
    initial_price = df['Adj Close'].iloc[0]
    final_price = df['Adj Close'].iloc[-1]
    num_years =  int(end_date[:4]) - int(start_date[:4])

    cagr = (final_price / initial_price) ** (1 / num_years) - 1

    return cagr

# Obter os componentes do índice Bovespa (IBOVESPA)
b3_tickers = si.tickers_ibovespa()

# Adicionar o sufixo .SA aos tickers
b3_tickers = [ticker + '.SA' for ticker in b3_tickers]
good_industries = ['Banks - Regional','Insurance','Utilities - Regulated Electric','Insurance - Life','Utilities - Renewable','Insurance - Reinsurance','Utilities - Regulated Water']
bad_industries = ['Airlines','Travel Services','Residential Construction','Department Stores','Specialty Retail','Household & Personal Products']
not_bad_tickers = []
indexs = []

# Verificar se a resposta contém dados
if b3_tickers:
    # Iterar sobre os tickers e imprimir cada um
    for ticker in b3_tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        info = stock.info
        income_statement = stock.income_stmt
        if income_statement is not None and 'Net Income' in income_statement:
            earnings_10y = income_statement.loc['Net Income'].tail(10)
        else:
            earnings_10y = pd.Series([0] * 10, name='Net Income')  # Initialize as a Series with zeros

            shares_outstanding = info.get('sharesOutstanding', 0)
        if shares_outstanding == 0:
          print(f"Não foi possível obter o número de ações em circulação para {ticker}")

        # Calcule o EPS para cada ano
        eps_10y = earnings_10y / shares_outstanding

        # Calcule a média do EPS dos últimos 10 anos
        average_eps_10y = eps_10y.mean()

        industry = info.get('industry', 'Indústria não encontrada')
        current_price = float(info.get('currentPrice','0'))
        eps = float(info.get('trailingEps', 0))

        #dataframe of dividends###################################
        dividend_history = stock.dividends
        dividends = dividend_history[:-1]
        dividends.index = dividends.index.date
        dividends_df = pd.DataFrame({
        'Data': pd.to_datetime(dividends.index).strftime('%d/%m/%Y'),
        'Dividendo por ação': dividends.values
        })
        dividends_df.set_index('Data', inplace=True)
        avarage_dividends_per_action_10y = dividends_df['Dividendo por ação'].mean()
        ###########################################################

        average_price_10y = hist['Close'].mean()
        average_dividends_10y = avarage_dividends_per_action_10y / average_price_10y if average_price_10y != 0 else 0
        dividend_payout_ratio = avarage_dividends_per_action_10y  /  average_eps_10y if  average_eps_10y != 0 else 0
        description = info.get('longBusinessSummary', 'Descrição não encontrada')
        pl = float(info.get('trailingPE','0'))
        dividend_yield = round(float(info.get('dividendYield', '0')),6)
        earnings_growth = float(info.get('earningsGrowth', '0'))
        company_time = get_company_age(ticker)
        cagr = c_cagr(ticker, '2020-01-03', '2023-03-03')
        roe  = calculate_roe(ticker)
        roic = calculate_roic(ticker)
        p_vpa = get_p_vpa(ticker)
        peg_ratio = float(info.get('pegRatio', '0'))
        
        #"removing terribles"
        if industry not in bad_industries and dividend_yield > 0.03 :

        #####+################ALGORITM1(Good companies)#################################################################

            alg1 = dividend_yield + roe*100*5 + roic +company_time + cagr + dividend_payout_ratio + average_dividends_10y
           
            if(industry in good_industries):
               alg1 += 10

        ######################ALGORITM2(Bad companies)##################################################################
            alg2 = 0
            if(alg1 >= 70)
                alg2 = p_vpa + peg_ratio + earnings_growth
        #########################################################################################################

            alg3 = (alg1 + alg2)/2
            
        ########################################################################################################################
            not_bad_tickers.append((alg3,ticker))
            print(f"Ticker: {ticker}[{current_price}]")
            print(f"  Indústria: {industry}")
            print(f"  Dividend Yield: {dividend_yield*100}%")
            print(f"  P/L : {pl}")
            print(f"  algoritimo : {alg3}")


else:
    print("Nenhum ticker encontrado para a B3.")

#sorting not_bad_tickers
not_bad_tickers_sorted = sorted(not_bad_tickers,reverse=True)
print("\n")

#print ticker's rank
for index, (alg, ticker) in enumerate(not_bad_tickers_sorted[:10],start=1):
    print(f"Índice: {index}.Ticker: {ticker}")
    print(f"Algoritmo: {alg}")
