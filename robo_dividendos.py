from yahoo_fin import stock_info as si
import pandas as pd
import yfinance as yf
    
#conseguir os ticker da B3
b3_tickers = si.tickers_ibovespa()
1
#sufixo .SA aos tickers pq no yfinace é assim
b3_tickers = [ticker + '.SA' for ticker in b3_tickers]

#industrias boas e ruins
good_industries = ['Banks - Regional','Insurance','Utilities - Regulated Electric','Insurance - Life','Utilities - Renewable','Insurance - Reinsurance','Utilities - Regulated Water']
bad_industries = ['Airlines','Travel Services','Residential Construction','Department Stores','Specialty Retail','Steel','Household & Personal Products']

#definindo e inicializando algumas coisas
not_bad_tickers = []
indexs = []
start_date = '2014-01-01'
end_date = '2024-08-20'

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
        his = stock.history(period='10y')['Close']
        start_price = his.iloc[0]
        end_price = his.iloc[-1]
        m2_after_price = his.iloc[-60]
        filtered_dividends = dividend.loc[start_date:end_date]
        dividends = filtered_dividends.resample('Y').sum()
        avg_dividend_yield = (dividends.mean() / stock.history(period='10y')['Close'].mean())*100
        cagr = (end_price / start_price) ** (1 / (int(end_date[:4]) - int(start_date[:4]))) - 1
    except:
        avg_dividend_yield = 0;
    

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
            price = stock.history(period='1d')['Close'].iloc[0]
            book_value_per_share = float(info.get('bookValue', 0))
            p_vpa = (price / book_value_per_share) if book_value_per_share != 0 else 0
            
           # pe_ratio = float(info.get('trailingPE', 0))
           #earnings_growth_rate = float(info.get('earningsGrowth', 0)) * 100  # Convertendo para porcentagem
           #peg_ratio = (pe_ratio / earnings_growth_rate) if earnings_growth_rate != 0 else 0
            alg1 = alg1*(100 - (p_vpa)*30 +(m2_after_price - end_price))/100
            #alg1 = (alg1*3 + (100 - (p_vpa)*30 +(m2_after_price - end_price))*3)/6
            
            not_bad_tickers.append((alg1,ticker))
            print(f"Ticker: {ticker}")
            print(f"  Indústria: {sector}")
            print(f"  10 anos dividend yield: {avg_dividend_yield}")
            print(f"  CAGR: {cagr}")
            print(f"  dividend payout: {dividend_payout_ratio_current}")
            print(f"  P/VPA: {p_vpa}")
            #print(f"  PEG Ratio: {peg_ratio}")
            print(f"  Algoritmo: {alg1}")
        
sorted_tickers = sorted(not_bad_tickers, reverse=True)
for index, (alg, ticker) in enumerate(sorted_tickers[:10],start=1):
    print(f"Índice: {index}.Ticker: {ticker}")
    print(f"Algoritmo: {alg}")