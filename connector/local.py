"""
fill the local config file
"""
import requests

def comprehensive_efficient(current_node, node):
    
    pass

def test_my_hardware(node):
    cpus = psutil.cpu_count()
    testarr = [196927]
    p = Pool(cpus) 
    start = time.time()
    for i in range(8):
        p.map(f, testarr*cpus)
    end = time.time()
    cpu_cal_time = (end - start) / cpus
    # psutil.virtual_memory().total
    # psutil.virtual_memory().used
    if cpu_cal_time > 20:
        cpu_cal_time = 20
    cpu_score = (20*1000 - int(cpu_cal_time * 1000)) * cpus
    mem = psutil.virtual_memory()
    free_mem = mem.free / 1024**3
    total_mem = mem.total / 1024**3
    pass

def parse_pc_str(s):
    """
        cpu_network_mem_diskspace
    """
    s=s.split('_')
    js ={}
    try:
        js['cpu'] = int(s[0])
        js['networkjs'] = int(s[1])
        js['mem'] = int(s[2])
        js['diskspace'] = int(s[3])
    except Exception as e:
        print(e)
        return {}
    return js

def json2str(js):
    s=''
    for k in js:
        s = s+js[k]+'_'
    return s.strip('_')
    



def test_my_network(node):
    res = speedtest.main()
    self.network_score = res.download + upload        
    pass

def fetch_my_ip():
    """
    this function will help to obtain this computer's ip and ip relate infomation, such as location
    """
    urls = [

    ]
    while(len(urls)> 0):
        try:
            url = urls[random.randint(0,len(urls)-1)]
            res = requests.get(url)
            break
        except Exception:
            urls.remove(url)
            continue



def f(x):
    return x**x