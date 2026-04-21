from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

AFIM_FUNDS = {
    'ahly_1':  {'name':'صندوق الأهلي الأول (نقدي)',    'type':'نقدي',     'yield':0.245,'min_m':0.01,'liquidity_days':1,  'risk':'low'},
    'ahly_2':  {'name':'صندوق الأهلي الثاني',          'type':'دخل ثابت', 'yield':0.221,'min_m':0.05,'liquidity_days':7,  'risk':'low'},
    'ahly_3':  {'name':'صندوق الأهلي الثالث (متوازن)', 'type':'متوازن',   'yield':0.192,'min_m':0.05,'liquidity_days':7,  'risk':'mid'},
    'bashaer': {'name':'صندوق بشائر (إسلامي)',          'type':'إسلامي',   'yield':0.234,'min_m':0.01,'liquidity_days':7,  'risk':'low'},
    'dahab':   {'name':'صندوق دهب (ذهب)',               'type':'سلع',      'yield':0.180,'min_m':0.1, 'liquidity_days':1,  'risk':'high'},
    'tbill':   {'name':'أذون خزانة',                    'type':'حكومي',    'yield':0.278,'min_m':0.1, 'liquidity_days':91, 'risk':'low'},
}

CLIENTS = [
    {'id':'C001','name':'شركة مصر للمقاولات','type':'corporate',
     'portfolio_m':84.5,'start_date':'2021-03-01','risk_profile':'low',
     'holdings':{'ahly_1':35.0,'tbill':22.0,'ahly_3':15.0},'cash_reserve_m':12.5},
    {'id':'C002','name':'مجموعة النيل للاستثمار','type':'corporate',
     'portfolio_m':120.0,'start_date':'2020-06-15','risk_profile':'mid',
     'holdings':{'ahly_1':30.0,'ahly_2':25.0,'tbill':40.0,'ahly_3':15.0},'cash_reserve_m':10.0},
    {'id':'C003','name':'د. أحمد المهندس','type':'individual',
     'portfolio_m':5.2,'start_date':'2023-01-10','risk_profile':'low',
     'holdings':{'bashaer':3.0,'ahly_1':1.5},'cash_reserve_m':0.7},
]

def get_performance(client):
    h = client['holdings']; total = sum(h.values())
    years = (datetime.today()-datetime.strptime(client['start_date'],'%Y-%m-%d')).days/365
    wy = sum(h[f]*AFIM_FUNDS[f]['yield'] for f in h if f in AFIM_FUNDS)/total
    ret_m = total*wy*min(years,1.0)
    history = []
    for i in range(6,0,-1):
        m = datetime.today()-timedelta(days=30*i)
        history.append({'month':m.strftime('%b %Y'),
                        'return_m':round(abs(total*(wy/12+np.random.normal(0,0.002))),3),
                        'portfolio_value_m':round(total+ret_m*(i/6),2)})
    holdings_detail = [
        {'fund_id':f,'name':AFIM_FUNDS[f]['name'],'type':AFIM_FUNDS[f]['type'],
         'amount_m':amt,'pct':round(amt/total*100,1),'yield_pct':round(AFIM_FUNDS[f]['yield']*100,1)}
        for f,amt in h.items() if f in AFIM_FUNDS]
    return {'client_id':client['id'],'client_name':client['name'],
            'portfolio_m':round(client['portfolio_m'],2),'total_invested_m':round(total,2),
            'cash_reserve_m':round(client.get('cash_reserve_m',0),2),
            'ytd_return_m':round(ret_m,3),'ytd_return_pct':round(wy*100,2),
            'monthly_yield_m':round(total*wy/12,3),'weighted_yield':round(wy*100,2),
            'holdings':holdings_detail,'monthly_history':history}

def simulate_investment(amount, duration, goal, risk):
    eligible = {k:v for k,v in AFIM_FUNDS.items() if amount>=v['min_m'] and
                v['risk'] in (['low'] if risk=='low' else ['low','mid'] if risk=='mid' else ['low','mid','high'])}
    if goal=='liquidity': eligible={k:v for k,v in eligible.items() if v['liquidity_days']<=7}
    elif goal=='islamic':  eligible={k:v for k,v in eligible.items() if v['type']=='إسلامي'}
    elif goal=='return':   eligible={k:v for k,v in eligible.items() if v['liquidity_days']<=duration*30}
    if not eligible: eligible=AFIM_FUNDS
    ranked=sorted(eligible.items(),key=lambda x:x[1]['yield'],reverse=True)
    bid,bf=ranked[0]
    return {'recommended_fund':bf['name'],'fund_type':bf['type'],
            'annual_yield_pct':round(bf['yield']*100,2),
            'expected_return_m':round(amount*bf['yield']*(duration/12),3),
            'effective_rate_pct':round(bf['yield']*(duration/12)*100,2),
            'liquidity_days':bf['liquidity_days'],
            'alternatives':[{'name':AFIM_FUNDS[k]['name'],'yield':round(v['yield']*100,2),
                              'expected_return_m':round(amount*v['yield']*(duration/12),3)}
                             for k,v in ranked[:3]]}

def gen_report(client_id):
    client=next((c for c in CLIENTS if c['id']==client_id),CLIENTS[0])
    perf=get_performance(client)
    cash_pct=perf['cash_reserve_m']/perf['portfolio_m']*100; ytd=perf['ytd_return_pct']
    recs=[]
    if cash_pct>20: recs.append({'priority':'HIGH','type':'reallocation','message':f'نسبة الاحتياطي ({cash_pct:.1f}%) مرتفعة. نوصي بتوجيه {cash_pct-15:.0f}% نحو أذون الخزانة (27.8%).'})
    if ytd<22:      recs.append({'priority':'MEDIUM','type':'yield_improvement','message':f'العائد الحالي ({ytd:.1f}%) أقل من المتوسط السوقي. إعادة التوزيع ترفع العائد ~1.2%.'})
    return {'report_id':f"RPT-{client_id}-{datetime.today().strftime('%Y%m')}",
            'generated_at':datetime.today().strftime('%d %B %Y'),
            'client_name':client['name'],
            'summary':{'portfolio_m':perf['portfolio_m'],'ytd_return_m':perf['ytd_return_m'],
                       'ytd_return_pct':ytd,'status':'ممتاز' if ytd>=24 else 'جيد' if ytd>=20 else 'يحتاج مراجعة'},
            'recommendations':recs,'performance':perf}

@app.route('/health')
def health(): return jsonify({'status':'running'})

@app.route('/clients')
def api_clients(): return jsonify([{'id':c['id'],'name':c['name'],'type':c['type']} for c in CLIENTS])

@app.route('/portfolio/<client_id>')
def api_portfolio(client_id):
    client=next((c for c in CLIENTS if c['id']==client_id),CLIENTS[0])
    return jsonify(get_performance(client))

@app.route('/simulate')
def api_simulate():
    return jsonify(simulate_investment(
        float(request.args.get('amount',20)), int(request.args.get('duration',3)),
        request.args.get('goal','return'), request.args.get('risk','low')))

@app.route('/report/<client_id>')
def api_report(client_id): return jsonify(gen_report(client_id))

@app.route('/funds')
def api_funds():
    return jsonify([{**v,'id':k,'yield_pct':round(v['yield']*100,2)} for k,v in AFIM_FUNDS.items()])

if __name__ == '__main__':
    print("="*50)
    print("  Cash Partner API — شغّال!")
    print("  http://localhost:5002")
    print("  افتح CashPartner.html في المتصفح")
    print("="*50)
    app.run(port=5002, debug=False)
