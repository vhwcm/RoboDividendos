from yahoo_fin import stock_info as si
import pandas as pd
import yfinance as yf
    

def atualizar_tempo(mes,ano):
    mes+=1
    if(mes>12):
        mes = 1
        ano+=1
    return mes,ano

def tempo_em_string(mes,ano):
    if(mes<10):
        mes = '0'+str(mes)
    return str(ano)+'-'+str(mes)+'-01',str(ano-10)+'-'+str(mes)+'-01'

#conseguir os ticker da B3
b3_tickers = si.tickers_ibovespa()

#sufixo .SA aos tickers pq no yfinace é assim
b3_tickers = [ticker + '.SA' for ticker in b3_tickers]

#industrias boas e ruins
good_industries = ['Banks - Regional','Insurance','Utilities - Regulated Electric','Insurance - Life','Utilities - Renewable','Insurance - Reinsurance','Utilities - Regulated Water']
bad_industries = ['Airlines','Travel Services','Residential Construction','Department Stores','Specialty Retail','Steel','Household & Personal Products']

#definindo e inicializando algumas coisas
not_bad_tickers = []
indexs = []
my_stocks =[]


#valores alteraveis
aporte_mensal = 1000
dinheiro_inicial = 0
dinheiro = dinheiro_inicial
current_month = 1
year = 2020
current_year = 2020
yearfinish = 2022



while current_year < yearfinish:
    # Iterar sobre os tickers
    for ticker in b3_tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        #obtendo setor
        sector  = info['industry']
        #todos os dividendos
        dividend = stock.dividends
        #calcular o médio dos últimos 10 anos
        try:
            str_temp,str_temp_10y = tempo_em_string(current_month,current_year)
            his = stock.history(start=str_temp_10y,end=str_temp)['Close']
            start_price = his.iloc[0]
            end_price = his.iloc[-1]
            m2_after_price = his.iloc[-60]
            filtered_dividends = dividend.loc[str_temp_10y:str_temp]
            dividends = filtered_dividends.resample('Y').sum()
            avg_dividend_yield = (dividends.mean() / stock.history(start=str_temp_10y,end=str_temp)['Close'].mean())*100
        except:
            avg_dividend_yield = 0;
        
        cagr = (end_price / start_price) ** (1 / 10) - 1

        #primeira peneira, retirando os setores ruins e com dividendos menores que 3% e cagr menor que 5%
        if sector not in bad_industries and avg_dividend_yield > 3 and cagr > 0.05:    
            financials = stock.financials.T
            financials = stock.financials.T    
            # Obter EPS mais recente
            eps = float(info.get('trailingEps', 0))
            # Obter dividendos pagos no último ano
            last_year_dividends = dividends.iloc[-1] if not dividends.empty else 0
            # Calcular o dividend payout ratio atual
            try:
                dividend_payout_ratio_current = (last_year_dividends / eps) if eps != 0 else None
            except Exception as e:
                print(f"Erro ao calcular dividend payout ratio atual para {ticker}: {e}")
                dividend_payout_ratio_current = 0
            
            #algoritmo
            ############################################################################################
            alg1 = (avg_dividend_yield*60*10 + cagr*20*500 + dividend_payout_ratio_current*20*100)/100
            if(sector not in good_industries):
                alg1 = alg1 * 0.8
            ###########################################################################################3
            if(alg1 > 0.6):
                book_value_per_share = None
                try:
                    for date in financials.columns:
                        if date.strftime('%Y-%m-%d') <= str_temp:
                            book_value_per_share = financials.loc['Total Stockholder Equity', date] / financials.loc['Shares Outstanding', date]
                            break

                    if book_value_per_share is not None:
                        book_value_per_share = float(book_value_per_share)
                        print(f"Book Value per Share em {str_temp}: {book_value_per_share}")
                    else:
                        print(f"Book Value per Share não disponível para a data {str_temp}")
                        book_value_per_share = float(info.get('bookValue', 0))
                        p_vpa = (end_price / book_value_per_share) if book_value_per_share != 0 else 0
                except:
                    p_vpa = 1  
            # pe_ratio = float(info.get('trailingPE', 0))
            #earnings_growth_rate = float(info.get('earningsGrowth', 0)) * 100  # Convertendo para porcentagem
            #peg_ratio = (pe_ratio / earnings_growth_rate) if earnings_growth_rate != 0 else 0
                #alg1 = alg1*((m2_after_price - end_price))/100
                alg1 = alg1*(100 - (p_vpa)*30 +(m2_after_price - end_price))/100
                #alg1 = (alg1*3 + (100 - (p_vpa)*30 +(m2_after_price - end_price))*3)/6
                
                not_bad_tickers.append((alg1,ticker,end_price,sector))
                print(f"Ticker: {ticker}")
                print(f"  Indústria: {sector}")
                print(f"  10 anos dividend yield: {avg_dividend_yield}")
                print(f"  CAGR: {cagr}")
                print(f"  dividend payout: {dividend_payout_ratio_current}")
                print(f"  P/VPA: {p_vpa}")
                #print(f"  PEG Ratio: {peg_ratio}")
                print(f"  Algoritmo: {alg1}")
            

    #ordenar os tickers
    sorted_tickers = sorted(not_bad_tickers, reverse=True)

    #printar os 10 melhores
    sectores = []
    for index, (alg, ticker,end_price,sector) in enumerate(sorted_tickers[:5],start=1):
        if sector not in sectores:
            sectores.append(sector)
    
    q_sectors = len(sectores)
    valor_por_setor = round(aporte_mensal/q_sectors,2)
    sectores.clear()
    for index, (alg, ticker,end_price,sector) in enumerate(sorted_tickers[:5],start=1):
        if(sector not in sectores):
            sectores.append(sector)
            qnt_stock = int(valor_por_setor/end_price)
            dinheiro += valor_por_setor - qnt_stock*end_price
            dinheiro -= qnt_stock*end_price
            my_stocks.append(ticker,qnt_stock)
            print(f"Índice: {index}.Ticker: {ticker}")
            print(f"Algoritmo: {alg}")
    print(my_stocks)
    #atualizar o tempo
    current_month,current_year = atualizar_tempo(current_month,current_year)


print(f"Dinheiro inicial: {dinheiro_inicial}")
print(f"Dinheiro final: {dinheiro}")

###############
# ############################################3
'''Melhores Empresas desse algoritmo:




'''

