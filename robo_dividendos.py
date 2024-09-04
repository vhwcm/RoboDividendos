from yahoo_fin import stock_info as si
import pandas as pd
import yfinance as yf
    

def get_dividendos(ticker,mes,ano,qnt_stock):
    stock = yf.Ticker(ticker)
    dividend = stock.dividends
    str_temp,k = tempo_em_string(mes,ano)
    mes_futuro = tempo_em_string_mes_futuro(mes,ano)
    filtered_dividends = dividend.loc[str_temp:mes_futuro]
    dividends = filtered_dividends.sum()*qnt_stock
    return dividends


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

def tempo_em_strign_10_anos(mes, ano):
    anos = []
    if(mes<10):
        str_mes = '0'+str(mes)
    else:
        str_mes = str(mes)
    
    ano -= 9
    for i in range(10):
        anos.append(str(ano)+'-'+str(mes)+'-01')
        ano += 1 
    
    return anos
    


def tempo_em_string_mes_futuro(mes,ano):
    if(mes == 12):
        mes = 1
        ano += 1
    else:
        mes += 1
    if(mes<10):
        mes = '0'+str(mes)
    return str(ano)+'-'+str(mes)+'-01'

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
my_stocks ={}


#valores alteraveis
aporte_mensal = 1000
dinheiro_inicial = 0
dinheiro = dinheiro_inicial
current_year = int(input("BACKTEST\nDigite o ano de ínicio: "))
current_month = int(input("Selecione o mês de início"))
yearfinish = int(input("Digite o ano final: "))
dividendos_totais = 0

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
            anos = tempo_em_strign_10_anos(current_month,current_year)
            y1_dividend_yield = [] 
            for i in range(9):
                filtered_dividends = dividend.loc[anos[i]:anos[i+1]]
                dividends = filtered_dividends.sum()
                y1_dividend_yield.append(dividends/stock.history(start=anos[i],end=anos[i+1])['Close'].mean())
            avg_dividend_yield = pd.Series(y1_dividend_yield).mean()*100    
        except:
            avg_dividend_yield = 0;

        print(avg_dividend_yield)
        
        cagr = (end_price / start_price) ** (1 / 10) - 1

        #primeira peneira, retirando os setores ruins e com dividendos menores que 3% e cagr menor que 5%
        if sector not in bad_industries and avg_dividend_yield > 3 and cagr > 0.05:    
            financials = stock.financials.T
            # Obter EPS mais recente
            eps = float(info.get('trailingEps', 0))
            # Obter dividendos pagos no último ano
            dividend = dividend.resample("YE").sum()
            last_year_dividends = dividend.iloc[-1] if not dividend.empty else 0
            # Calcular o dividend payout ratio atual
            try:
                dividend_payout_ratio_current = (last_year_dividends / eps) if eps != 0 else None
            except Exception as e:
                print(f"Erro ao calcular dividend payout ratio atual para {ticker}: {e}")
                dividend_payout_ratio_current = 0
            
            #algoritmo
            ############################################################################################
            x = avg_dividend_yield - 6
            alg_avg_dividend_yield = (1 + (x/abs(x))*(x**2/(15+x**2))**0.3)/2
            x = cagr - 0.1
            x = m2_after_price/end_price 
            alg_queda = (x/abs(x))*(x**4/(1+(x**4)))
            alg_cagr = (1 + (x/abs(x))*(x**2/(0.07+x**2))**0.5)/2
            x = dividend_payout_ratio_current*100 - 25
            alg_dividend_payout = (1 + (x/abs(x))*(x**2/(700 + x**2)))/2
            alg = alg_avg_dividend_yield*0.6 + alg_cagr*0.1 + alg_dividend_payout*0.1 + alg_queda*0.2 
            print("Ticker: ", ticker)
            print("Dividend yield:", avg_dividend_yield)
            print("alg dividend yirld", alg_avg_dividend_yield)
            print("cagr: ", cagr)
            print("alg cagr: ", alg_cagr)
            print("dividend payout ", dividend_payout_ratio_current)
            print("alg payout ", alg_dividend_payout)
            print("alg_queda" , alg_queda)
            print("alg final: ", alg,"\n\n")
            ###########################################################################################3
            if(sector not in good_industries):
                alg = alg * 0.9
            not_bad_tickers.append((alg,ticker,end_price,sector))
        else:
            b3_tickers.remove(ticker)
                
            '''if(alg > 0.5):
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
                    p_vpa = 2  
                #pe_ratio = float(info.get('trailingPE', 0))
                #earnings_growth_rate = float(info.get('earningsGrowth', 0)) * 100  # Convertendo para porcentagem
                #peg_ratio = (pe_ratio / earnings_growth_rate) if earnings_growth_rate != 0 else 0
                '''                
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
    print("COMPRAS DO MÊS:")
    for index, (alg, ticker,end_price,sector) in enumerate(sorted_tickers[:5],start=1):
        if(sector not in sectores):            
            sectores.append(sector)
            qnt_stock = int(valor_por_setor/end_price)
            dinheiro += valor_por_setor - qnt_stock*end_price
            dinheiro_inicial += 1000
            if(ticker not in my_stocks):
                my_stocks[ticker] = qnt_stock
            else:
                my_stocks[ticker] += qnt_stock
            print(f"    Índice: {index}.Ticker: {ticker}")
            print(f"    quantidade de ações: {qnt_stock}")
            print(f"    Preço: {end_price}")
            print(f"    Setor: {sector}")
            print(f"    Algoritmo: {alg}")
            print("\n")

    print()
    aporte_mensal = 1000
    for st, qnt in my_stocks.items():
        dividendos_recebidos = get_dividendos(st,current_month,current_year,qnt)
        aporte_mensal += dividendos_recebidos
        dividendos_totais += dividendos_recebidos
        print(f"CARTEIRA COMPLETA DO MÊS:")               
        print(f"    Data: {str_temp}")       
        print(f"    Dividendos recebidos: {dividendos_recebidos}")
        print(f"    Aporte mensal: {aporte_mensal}")
        print(f"    {st}: {qnt}")
        print("\n\n")
    #atualizar o tempo
    current_month,current_year = atualizar_tempo(current_month,current_year)



for st, qnt in my_stocks.items():
    stock = yf.Ticker(st)
    stock_price = stock.history(period='1d')['Close'].iloc[-1]
    dinheiro += qnt*stock_price
    print(f"{st}: {qnt}")

print(f"Dinheiro Investido do bolso: {dinheiro_inicial}")
print(f"Dinheiro final: {dinheiro}")

###############
#############################################3


